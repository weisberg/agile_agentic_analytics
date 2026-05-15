"""Markov chain navigation path analysis and conversion path identification.

Builds second-order (bigram) Markov chain transition matrices from
session-level page sequences. Identifies high-conversion paths, dead-end
pages, and unexpected navigation loops.

Dependencies:
    - pandas
    - numpy
    - scipy (sparse matrices)
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# Sentinel page labels for session boundaries.
START_PAGE = "__START__"
CONVERT_PAGE = "__CONVERT__"
EXIT_PAGE = "__EXIT__"


@dataclass
class PathAnalysisConfig:
    """Configuration for Markov chain path analysis.

    Attributes:
        order: Markov chain order. Default 2 (bigram / second-order).
        beam_width: Beam width for path enumeration. Default 50.
        top_k_paths: Number of top conversion paths to report. Default 10.
        min_page_views: Minimum total pageviews for a page to be included
            as a distinct state. Pages below this threshold are grouped
            into an "Other" category. Default 50.
        exit_rate_percentile: Percentile threshold for dead-end detection.
            Pages with exit rates above this percentile are flagged.
            Default 90.
        loop_probability_threshold: Minimum transition probability for a
            back-transition to be considered a loop. Default 0.1.
        terminal_pages: Set of page paths that are natural terminal pages
            and should not be flagged as dead ends (e.g., "/thank-you").
    """

    order: int = 2
    beam_width: int = 50
    top_k_paths: int = 10
    min_page_views: int = 50
    exit_rate_percentile: float = 90.0
    loop_probability_threshold: float = 0.1
    terminal_pages: set[str] = field(default_factory=set)


@dataclass
class NavigationPath:
    """A ranked navigation path to conversion.

    Attributes:
        pages: Ordered list of page paths from entry to conversion.
        probability: Product of transition probabilities along the path.
        session_count: Number of sessions that followed this exact path.
        conversion_rate: Fraction of sessions on this path that converted.
    """

    pages: list[str]
    probability: float
    session_count: int
    conversion_rate: float


@dataclass
class PageAnalysis:
    """Analysis results for a single page.

    Attributes:
        page_path: The page URL path.
        exit_rate: Fraction of sessions that ended on this page.
        weighted_exit_rate: Exit rate weighted by conversion proximity.
        is_dead_end: True if the page is flagged as a dead end.
        removal_effect: Fractional drop in conversion probability when
            this page is removed from the Markov chain.
        avg_steps_to_conversion: Average number of page transitions from
            this page to conversion.
    """

    page_path: str
    exit_rate: float
    weighted_exit_rate: float
    is_dead_end: bool
    removal_effect: float
    avg_steps_to_conversion: float | None


@dataclass
class LoopDetection:
    """A detected navigation loop.

    Attributes:
        page_a: First page in the loop.
        page_b: Second page in the loop.
        loop_probability: Probability of transitioning back from B to A.
        affected_sessions: Number of sessions containing this loop.
        conversion_rate_with_loop: Conversion rate for sessions with loop.
        conversion_rate_without_loop: Conversion rate for sessions without.
    """

    page_a: str
    page_b: str
    loop_probability: float
    affected_sessions: int
    conversion_rate_with_loop: float
    conversion_rate_without_loop: float


def parse_sessions(
    events_df: pd.DataFrame,
    session_id_column: str = "session_id",
    page_column: str = "page_path",
    timestamp_column: str = "timestamp",
    conversion_event: str = "purchase",
    event_name_column: str = "event_name",
) -> list[tuple[list[str], bool]]:
    """Parse event-level data into session page sequences.

    Args:
        events_df: DataFrame of event-level data.
        session_id_column: Column identifying the session.
        page_column: Column containing the page path.
        timestamp_column: Column with event timestamps for ordering.
        conversion_event: Event name that indicates conversion.
        event_name_column: Column containing the event name.

    Returns:
        List of (page_sequence, converted) tuples. Each page_sequence is
        an ordered list of page paths visited in the session. converted
        is True if the session contained a conversion event.
    """
    df = events_df.copy()
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    df = df.sort_values([session_id_column, timestamp_column])

    sessions: list[tuple[list[str], bool]] = []

    for session_id, group in df.groupby(session_id_column):
        # Check if session contains a conversion event.
        converted = False
        if event_name_column in group.columns:
            converted = (group[event_name_column] == conversion_event).any()

        # Extract ordered page sequence, removing consecutive duplicates.
        pages_raw = group[page_column].dropna().tolist()
        pages: list[str] = []
        for page in pages_raw:
            page_str = str(page)
            if not pages or pages[-1] != page_str:
                pages.append(page_str)

        if pages:
            sessions.append((pages, converted))

    return sessions


def aggregate_low_traffic_pages(
    sessions: list[tuple[list[str], bool]],
    min_page_views: int,
) -> list[tuple[list[str], bool]]:
    """Replace low-traffic pages with an 'Other' category.

    Pages with total views below min_page_views across all sessions are
    replaced with the label "__OTHER__" to keep the state space manageable.

    Args:
        sessions: List of (page_sequence, converted) tuples.
        min_page_views: Minimum pageview threshold.

    Returns:
        Modified sessions with low-traffic pages replaced.
    """
    # Count page frequencies across all sessions.
    page_counts: Counter[str] = Counter()
    for pages, _ in sessions:
        for page in pages:
            page_counts[page] += 1

    # Identify low-traffic pages.
    low_traffic = {page for page, count in page_counts.items() if count < min_page_views}

    if not low_traffic:
        return sessions

    # Replace low-traffic pages, collapsing consecutive "__OTHER__".
    result: list[tuple[list[str], bool]] = []
    for pages, converted in sessions:
        new_pages: list[str] = []
        for page in pages:
            replacement = "__OTHER__" if page in low_traffic else page
            if not new_pages or new_pages[-1] != replacement:
                new_pages.append(replacement)
        if new_pages:
            result.append((new_pages, converted))

    return result


def build_transition_matrix(
    sessions: list[tuple[list[str], bool]],
    order: int = 2,
) -> dict[tuple[str, ...], dict[str, float]]:
    """Build a Markov chain transition matrix from session page sequences.

    For second-order chains, each state is a tuple of the last `order`
    pages. Transition probabilities are normalized per state.

    Args:
        sessions: List of (page_sequence, converted) tuples.
        order: Markov chain order (number of prior pages in each state).

    Returns:
        Dict mapping state tuples to dicts of {next_page: probability}.
        Includes START and CONVERT/EXIT sentinel states.
    """
    counts: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for pages, converted in sessions:
        # Build the full sequence with sentinels.
        # Prepend START tokens and append CONVERT or EXIT.
        full_seq = [START_PAGE] * order + pages + [CONVERT_PAGE if converted else EXIT_PAGE]

        # Extract transitions: state = (full_seq[i], ..., full_seq[i+order-1]) -> full_seq[i+order]
        for i in range(len(full_seq) - order):
            state = tuple(full_seq[i : i + order])
            next_page = full_seq[i + order]
            counts[state][next_page] += 1

    # Normalize to probabilities.
    transition_matrix: dict[tuple[str, ...], dict[str, float]] = {}
    for state, transitions in counts.items():
        total = sum(transitions.values())
        if total > 0:
            transition_matrix[state] = {page: count / total for page, count in transitions.items()}

    return transition_matrix


def _compute_conversion_probability(
    transition_matrix: dict[tuple[str, ...], dict[str, float]],
    order: int = 2,
    max_steps: int = 100,
) -> float:
    """Compute overall conversion probability from START via absorbing Markov chain."""
    start_state = tuple([START_PAGE] * order)

    # BFS/probability propagation through the chain.
    # state -> probability of being in that state
    current_probs: dict[tuple[str, ...], float] = {start_state: 1.0}
    total_convert_prob = 0.0

    for _ in range(max_steps):
        next_probs: dict[tuple[str, ...], float] = defaultdict(float)
        for state, state_prob in current_probs.items():
            if state_prob < 1e-12:
                continue
            transitions = transition_matrix.get(state, {})
            if not transitions:
                continue
            for next_page, trans_prob in transitions.items():
                if next_page == CONVERT_PAGE:
                    total_convert_prob += state_prob * trans_prob
                elif next_page == EXIT_PAGE:
                    pass  # Absorbed — no further transitions.
                else:
                    # Build next state by shifting window.
                    next_state = state[1:] + (next_page,)
                    next_probs[next_state] += state_prob * trans_prob

        if not next_probs:
            break
        current_probs = dict(next_probs)

    return total_convert_prob


def find_top_conversion_paths(
    transition_matrix: dict[tuple[str, ...], dict[str, float]],
    beam_width: int = 50,
    top_k: int = 10,
    order: int = 2,
) -> list[NavigationPath]:
    """Find the highest-probability paths to conversion via beam search.

    Args:
        transition_matrix: Markov chain transition probabilities.
        beam_width: Number of candidate paths to maintain at each step.
        top_k: Number of top paths to return.
        order: Markov chain order (for constructing the start state).

    Returns:
        Top K NavigationPath objects sorted by probability descending.
    """
    start_state = tuple([START_PAGE] * order)

    # Each beam entry: (neg_log_prob, path_pages, current_state)
    # Using neg log probability for the heap (min-heap gives highest prob).
    beam: list[tuple[float, list[str], tuple[str, ...]]] = [(0.0, [], start_state)]
    completed: list[tuple[float, list[str]]] = []

    max_path_length = 50  # Safety limit.

    for _ in range(max_path_length):
        candidates: list[tuple[float, list[str], tuple[str, ...]]] = []

        for neg_log_prob, path_pages, state in beam:
            transitions = transition_matrix.get(state, {})
            if not transitions:
                continue

            for next_page, trans_prob in transitions.items():
                if trans_prob <= 0:
                    continue

                new_neg_log = neg_log_prob - np.log(trans_prob)

                if next_page == CONVERT_PAGE:
                    completed.append((new_neg_log, path_pages))
                elif next_page == EXIT_PAGE:
                    pass  # Dead path — discard.
                else:
                    new_pages = path_pages + [next_page]
                    next_state = state[1:] + (next_page,)
                    candidates.append((new_neg_log, new_pages, next_state))

        if not candidates:
            break

        # Keep only top beam_width candidates (lowest neg_log_prob = highest prob).
        candidates.sort(key=lambda x: x[0])
        beam = candidates[:beam_width]

    # Sort completed paths by probability (lowest neg_log_prob first).
    completed.sort(key=lambda x: x[0])
    top_paths = completed[:top_k]

    result: list[NavigationPath] = []
    for neg_log_prob, pages in top_paths:
        prob = np.exp(-neg_log_prob)
        result.append(
            NavigationPath(
                pages=pages,
                probability=float(prob),
                session_count=0,  # Populated later if session data is available.
                conversion_rate=0.0,
            )
        )

    return result


def _count_path_sessions(
    sessions: list[tuple[list[str], bool]],
    nav_paths: list[NavigationPath],
) -> list[NavigationPath]:
    """Populate session_count and conversion_rate on NavigationPath objects."""
    # Build a lookup of path tuple -> index
    path_lookup: dict[tuple[str, ...], int] = {}
    for i, np_ in enumerate(nav_paths):
        path_lookup[tuple(np_.pages)] = i

    path_total: dict[int, int] = defaultdict(int)
    path_converted: dict[int, int] = defaultdict(int)

    for pages, converted in sessions:
        key = tuple(pages)
        if key in path_lookup:
            idx = path_lookup[key]
            path_total[idx] += 1
            if converted:
                path_converted[idx] += 1
        # Also check if session pages are a subsequence match — but exact
        # match is most meaningful for Markov path analysis.

    for idx, np_ in enumerate(nav_paths):
        np_.session_count = path_total.get(idx, 0)
        total = path_total.get(idx, 0)
        np_.conversion_rate = path_converted.get(idx, 0) / total if total > 0 else 0.0

    return nav_paths


def compute_removal_effect(
    transition_matrix: dict[tuple[str, ...], dict[str, float]],
    page: str,
    baseline_conversion_prob: float,
    order: int = 2,
) -> float:
    """Compute the removal effect of a page on conversion probability.

    Redirects all transitions through states containing the page to EXIT,
    then recomputes the overall conversion probability.

    Args:
        transition_matrix: Original Markov chain transition probabilities.
        page: Page path to remove.
        baseline_conversion_prob: Conversion probability with all pages.
        order: Markov chain order.

    Returns:
        Removal effect as a fraction (0.0 to 1.0). Higher values indicate
        the page is more critical to conversion.
    """
    if baseline_conversion_prob <= 0:
        return 0.0

    # Build modified transition matrix: for any state containing the page,
    # redirect all outgoing transitions to EXIT.
    modified: dict[tuple[str, ...], dict[str, float]] = {}
    for state, transitions in transition_matrix.items():
        if page in state:
            # Redirect: all probability mass goes to EXIT.
            modified[state] = {EXIT_PAGE: 1.0}
        else:
            # Also redirect any transitions that go TO the removed page
            # to EXIT instead.
            new_trans: dict[str, float] = {}
            redirected = 0.0
            for next_page, prob in transitions.items():
                if next_page == page:
                    redirected += prob
                else:
                    new_trans[next_page] = prob
            if redirected > 0:
                new_trans[EXIT_PAGE] = new_trans.get(EXIT_PAGE, 0.0) + redirected
            modified[state] = new_trans

    modified_prob = _compute_conversion_probability(modified, order)

    removal_effect = (baseline_conversion_prob - modified_prob) / baseline_conversion_prob
    return max(0.0, min(1.0, removal_effect))


def _compute_avg_steps_to_conversion(
    transition_matrix: dict[tuple[str, ...], dict[str, float]],
    page: str,
    order: int = 2,
    max_steps: int = 100,
) -> float | None:
    """Compute average steps from states containing a page to CONVERT."""
    # Find all states containing this page.
    start_states = [s for s in transition_matrix if page in s]
    if not start_states:
        return None

    total_weighted_steps = 0.0
    total_weight = 0.0

    for start_state in start_states:
        # BFS propagation.
        current: dict[tuple[str, ...], float] = {start_state: 1.0}
        for step in range(1, max_steps + 1):
            next_probs: dict[tuple[str, ...], float] = defaultdict(float)
            for state, prob in current.items():
                transitions = transition_matrix.get(state, {})
                for next_page, tp in transitions.items():
                    if next_page == CONVERT_PAGE:
                        total_weighted_steps += step * prob * tp
                        total_weight += prob * tp
                    elif next_page != EXIT_PAGE:
                        next_state = state[1:] + (next_page,)
                        next_probs[next_state] += prob * tp
            current = dict(next_probs)
            if not current:
                break

    if total_weight <= 0:
        return None
    return total_weighted_steps / total_weight


def detect_dead_ends(
    transition_matrix: dict[tuple[str, ...], dict[str, float]],
    sessions: list[tuple[list[str], bool]],
    config: PathAnalysisConfig,
) -> list[PageAnalysis]:
    """Identify dead-end pages with high exit rates.

    Args:
        transition_matrix: Markov chain transition probabilities.
        sessions: Parsed session data for exit rate computation.
        config: Path analysis configuration.

    Returns:
        List of PageAnalysis objects for pages flagged as dead ends.
    """
    # Compute per-page exit rates from session data.
    exit_counts: Counter[str] = Counter()
    last_page_counts: Counter[str] = Counter()
    page_view_counts: Counter[str] = Counter()

    for pages, converted in sessions:
        for page in pages:
            page_view_counts[page] += 1
        # The last page in the sequence is the exit page (unless converted).
        if pages and not converted:
            exit_counts[pages[-1]] += 1
        if pages:
            last_page_counts[pages[-1]] += 1

    # Compute exit rates.
    all_pages = set(page_view_counts.keys()) - {START_PAGE, CONVERT_PAGE, EXIT_PAGE, "__OTHER__"}
    page_exit_rates: dict[str, float] = {}

    for page in all_pages:
        total_as_last = last_page_counts.get(page, 0)
        exits = exit_counts.get(page, 0)
        # Exit rate = exits / times page appeared as last page in non-converting sessions
        # More accurately: exits / total sessions where this page was visited
        total_views = page_view_counts.get(page, 0)
        page_exit_rates[page] = exits / total_views if total_views > 0 else 0.0

    if not page_exit_rates:
        return []

    # Determine the percentile threshold.
    rates = list(page_exit_rates.values())
    threshold = float(np.percentile(rates, config.exit_rate_percentile))

    # Compute baseline conversion probability for removal effects.
    baseline_conv = _compute_conversion_probability(transition_matrix, config.order)

    dead_ends: list[PageAnalysis] = []
    for page, exit_rate in page_exit_rates.items():
        if exit_rate < threshold:
            continue
        if page in config.terminal_pages:
            continue

        avg_steps = _compute_avg_steps_to_conversion(transition_matrix, page, config.order)
        proximity_weight = 1.0 / (1.0 + avg_steps) if avg_steps is not None else 0.0
        weighted_exit_rate = exit_rate * proximity_weight

        removal = compute_removal_effect(transition_matrix, page, baseline_conv, config.order)

        dead_ends.append(
            PageAnalysis(
                page_path=page,
                exit_rate=exit_rate,
                weighted_exit_rate=weighted_exit_rate,
                is_dead_end=True,
                removal_effect=removal,
                avg_steps_to_conversion=avg_steps,
            )
        )

    # Sort by weighted exit rate descending.
    dead_ends.sort(key=lambda p: p.weighted_exit_rate, reverse=True)
    return dead_ends


def detect_loops(
    transition_matrix: dict[tuple[str, ...], dict[str, float]],
    sessions: list[tuple[list[str], bool]],
    config: PathAnalysisConfig,
) -> list[LoopDetection]:
    """Detect unexpected navigation loops between page pairs.

    A loop is flagged when the back-transition probability exceeds the
    threshold and sessions containing the loop have significantly lower
    conversion rates.

    Args:
        transition_matrix: Markov chain transition probabilities.
        sessions: Parsed session data for conversion rate comparison.
        config: Path analysis configuration.

    Returns:
        List of LoopDetection objects for flagged loops.
    """
    sentinel_pages = {START_PAGE, CONVERT_PAGE, EXIT_PAGE, "__OTHER__"}

    # Scan for back-transitions: state (A, B) -> A with probability > threshold.
    candidate_loops: list[tuple[str, str, float]] = []

    for state, transitions in transition_matrix.items():
        if len(state) < 2:
            continue
        page_a = state[-2]  # The page before current.
        page_b = state[-1]  # Current page.

        if page_a in sentinel_pages or page_b in sentinel_pages:
            continue
        if page_a == page_b:
            continue

        # Check if there's a back-transition to page_a.
        back_prob = transitions.get(page_a, 0.0)
        if back_prob >= config.loop_probability_threshold:
            candidate_loops.append((page_a, page_b, back_prob))

    if not candidate_loops:
        return []

    # For each candidate loop, segment sessions and compare conversion rates.
    loops: list[LoopDetection] = []

    for page_a, page_b, loop_prob in candidate_loops:
        sessions_with_loop = 0
        sessions_with_loop_converted = 0
        sessions_without_loop = 0
        sessions_without_loop_converted = 0

        for pages, converted in sessions:
            has_loop = False
            for i in range(len(pages) - 2):
                if pages[i] == page_a and pages[i + 1] == page_b and pages[i + 2] == page_a:
                    has_loop = True
                    break

            if has_loop:
                sessions_with_loop += 1
                if converted:
                    sessions_with_loop_converted += 1
            else:
                sessions_without_loop += 1
                if converted:
                    sessions_without_loop_converted += 1

        if sessions_with_loop == 0:
            continue

        cr_with = sessions_with_loop_converted / sessions_with_loop
        cr_without = sessions_without_loop_converted / sessions_without_loop if sessions_without_loop > 0 else 0.0

        # Z-test for difference in proportions.
        n1 = sessions_with_loop
        n2 = sessions_without_loop
        if n2 > 0 and (n1 + n2) > 0:
            p_pool = (sessions_with_loop_converted + sessions_without_loop_converted) / (n1 + n2)
            if p_pool > 0 and p_pool < 1:
                se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
                if se > 0:
                    z_stat = (cr_with - cr_without) / se
                    # Only flag if loop sessions have significantly LOWER conversion.
                    # One-sided test: z < -1.645 for p < 0.05.
                    if z_stat >= -1.645:
                        continue  # Not significantly lower — skip.

        loops.append(
            LoopDetection(
                page_a=page_a,
                page_b=page_b,
                loop_probability=loop_prob,
                affected_sessions=sessions_with_loop,
                conversion_rate_with_loop=cr_with,
                conversion_rate_without_loop=cr_without,
            )
        )

    # Sort by affected sessions descending.
    loops.sort(key=lambda l: l.affected_sessions, reverse=True)
    return loops


def run_path_analysis(
    input_path: Path,
    output_path: Path,
    config: PathAnalysisConfig | None = None,
) -> dict[str, Any]:
    """Run the full navigation path analysis pipeline.

    Args:
        input_path: Path to the events CSV/JSON file.
        output_path: Path to write the navigation_paths.json output.
        config: Optional path analysis config (uses defaults if None).

    Returns:
        Dict with keys "top_paths", "dead_ends", "loops", and
        "page_analyses" containing the analysis results.
    """
    if config is None:
        config = PathAnalysisConfig()

    # Load events data.
    suffix = input_path.suffix.lower()
    if suffix == ".json":
        events_df = pd.read_json(input_path)
    else:
        events_df = pd.read_csv(input_path)

    # Parse sessions.
    sessions = parse_sessions(events_df)

    # Aggregate low-traffic pages.
    sessions = aggregate_low_traffic_pages(sessions, config.min_page_views)

    # Build transition matrix.
    transition_matrix = build_transition_matrix(sessions, config.order)

    # Find top conversion paths.
    top_paths = find_top_conversion_paths(transition_matrix, config.beam_width, config.top_k_paths, config.order)
    top_paths = _count_path_sessions(sessions, top_paths)

    # Compute baseline conversion probability.
    baseline_conv = _compute_conversion_probability(transition_matrix, config.order)

    # Compute page-level analyses (removal effect, avg steps) for all pages.
    all_pages: set[str] = set()
    for pages, _ in sessions:
        all_pages.update(pages)
    all_pages -= {START_PAGE, CONVERT_PAGE, EXIT_PAGE, "__OTHER__"}

    page_analyses: list[PageAnalysis] = []
    # First compute exit rates.
    exit_counts: Counter[str] = Counter()
    view_counts: Counter[str] = Counter()
    for pages, converted in sessions:
        for p in pages:
            view_counts[p] += 1
        if pages and not converted:
            exit_counts[pages[-1]] += 1

    for page in all_pages:
        views = view_counts.get(page, 0)
        exits = exit_counts.get(page, 0)
        exit_rate = exits / views if views > 0 else 0.0

        avg_steps = _compute_avg_steps_to_conversion(transition_matrix, page, config.order)
        proximity_weight = 1.0 / (1.0 + avg_steps) if avg_steps is not None else 0.0
        weighted_exit_rate = exit_rate * proximity_weight

        removal = compute_removal_effect(transition_matrix, page, baseline_conv, config.order)

        exit_rate_threshold = (
            float(
                np.percentile(
                    [exit_counts.get(p, 0) / view_counts.get(p, 1) for p in all_pages],
                    config.exit_rate_percentile,
                )
            )
            if all_pages
            else 0.0
        )

        is_dead = exit_rate >= exit_rate_threshold and page not in config.terminal_pages

        page_analyses.append(
            PageAnalysis(
                page_path=page,
                exit_rate=exit_rate,
                weighted_exit_rate=weighted_exit_rate,
                is_dead_end=is_dead,
                removal_effect=removal,
                avg_steps_to_conversion=avg_steps,
            )
        )

    page_analyses.sort(key=lambda p: p.removal_effect, reverse=True)

    # Detect dead ends and loops.
    dead_ends = detect_dead_ends(transition_matrix, sessions, config)
    loops = detect_loops(transition_matrix, sessions, config)

    # Build output.
    results: dict[str, Any] = {
        "baseline_conversion_probability": baseline_conv,
        "top_paths": [asdict(p) for p in top_paths],
        "dead_ends": [asdict(d) for d in dead_ends],
        "loops": [asdict(l) for l in loops],
        "page_analyses": [asdict(pa) for pa in page_analyses],
    }

    # Write to output.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Markov chain path analysis")
    parser.add_argument("--input", default="workspace/raw/events.csv")
    parser.add_argument("--output", default="workspace/analysis/navigation_paths.json")
    parser.add_argument("--beam-width", type=int, default=50)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--min-page-views", type=int, default=50)

    args = parser.parse_args()

    path_config = PathAnalysisConfig(
        beam_width=args.beam_width,
        top_k_paths=args.top_k,
        min_page_views=args.min_page_views,
    )

    results = run_path_analysis(
        input_path=Path(args.input),
        output_path=Path(args.output),
        config=path_config,
    )
    print(f"Found {len(results.get('top_paths', []))} conversion paths")
    print(f"Detected {len(results.get('dead_ends', []))} dead-end pages")
    print(f"Detected {len(results.get('loops', []))} navigation loops")
