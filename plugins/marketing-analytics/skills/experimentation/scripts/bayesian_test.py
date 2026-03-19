"""Bayesian A/B test analysis.

Posterior computation, probability of being best, and expected loss using
conjugate prior models: Beta-Binomial for conversions and
Normal-Inverse-Gamma for continuous metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import stats


@dataclass
class BetaPosterior:
    """Beta posterior distribution for a conversion rate.

    Attributes:
        alpha: Beta distribution alpha parameter (successes + prior alpha).
        beta: Beta distribution beta parameter (failures + prior beta).
        mean: Posterior mean.
        variance: Posterior variance.
        credible_interval_95: 95% highest-density credible interval.
    """

    alpha: float
    beta: float
    mean: float
    variance: float
    credible_interval_95: Tuple[float, float]


@dataclass
class NormalInverseGammaPosterior:
    """Normal-Inverse-Gamma posterior for a continuous metric.

    Attributes:
        mu: Posterior mean of the location parameter.
        nu: Posterior effective sample size.
        alpha: Posterior shape parameter.
        beta: Posterior scale parameter.
        mean: Posterior predictive mean.
        credible_interval_95: 95% credible interval for the mean.
    """

    mu: float
    nu: float
    alpha: float
    beta: float
    mean: float
    credible_interval_95: Tuple[float, float]


@dataclass
class BayesianResult:
    """Result of a Bayesian A/B test analysis.

    Attributes:
        metric_name: Name of the metric analyzed.
        variant_posteriors: Dict mapping variant name to its posterior.
        prob_being_best: Dict mapping variant name to probability of being best.
        expected_loss: Dict mapping variant name to expected loss if chosen.
        lift_distribution_summary: Summary stats for the treatment-control lift.
        credible_interval_lift: 95% credible interval for the lift.
        risk_reward: Tuple of (expected_upside, expected_downside).
    """

    metric_name: str
    variant_posteriors: Dict[str, BetaPosterior | NormalInverseGammaPosterior]
    prob_being_best: Dict[str, float]
    expected_loss: Dict[str, float]
    lift_distribution_summary: Dict[str, float]
    credible_interval_lift: Tuple[float, float]
    risk_reward: Tuple[float, float]


def compute_beta_posterior(
    successes: int,
    total: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
) -> BetaPosterior:
    """Compute the Beta posterior for a conversion rate.

    Args:
        successes: Number of conversions observed.
        total: Total number of observations.
        prior_alpha: Beta prior alpha parameter. Default 1.0 (uniform).
        prior_beta: Beta prior beta parameter. Default 1.0 (uniform).

    Returns:
        BetaPosterior with updated parameters and summary statistics.

    Raises:
        ValueError: If successes > total or parameters are negative.
    """
    # TODO: Validate inputs
    # TODO: Compute posterior parameters: alpha_post = prior_alpha + successes,
    #   beta_post = prior_beta + (total - successes)
    # TODO: Compute posterior mean: alpha_post / (alpha_post + beta_post)
    # TODO: Compute posterior variance
    # TODO: Compute 95% credible interval using scipy.stats.beta.ppf
    # TODO: Return BetaPosterior
    raise NotImplementedError("Beta posterior computation not yet implemented")


def compute_nig_posterior(
    values: np.ndarray,
    prior_mu: float = 0.0,
    prior_nu: float = 0.01,
    prior_alpha: float = 0.01,
    prior_beta: float = 0.01,
) -> NormalInverseGammaPosterior:
    """Compute the Normal-Inverse-Gamma posterior for a continuous metric.

    Args:
        values: Array of observed metric values.
        prior_mu: Prior mean. Default 0.0.
        prior_nu: Prior effective sample size. Default 0.01 (weakly informative).
        prior_alpha: Prior shape parameter. Default 0.01.
        prior_beta: Prior scale parameter. Default 0.01.

    Returns:
        NormalInverseGammaPosterior with updated parameters.

    Raises:
        ValueError: If values is empty or prior parameters are invalid.
    """
    # TODO: Validate inputs
    # TODO: Compute sufficient statistics: n, y_bar, sum of squared deviations
    # TODO: Update posterior parameters:
    #   nu_n = prior_nu + n
    #   mu_n = (prior_nu * prior_mu + n * y_bar) / nu_n
    #   alpha_n = prior_alpha + n / 2
    #   beta_n = prior_beta + 0.5 * SS + (n * prior_nu * (y_bar - prior_mu)^2) / (2 * nu_n)
    # TODO: Compute posterior predictive mean and credible interval
    # TODO: Return NormalInverseGammaPosterior
    raise NotImplementedError("NIG posterior computation not yet implemented")


def probability_of_being_best(
    posteriors: Dict[str, BetaPosterior | NormalInverseGammaPosterior],
    n_simulations: int = 100_000,
    random_seed: int = 42,
) -> Dict[str, float]:
    """Compute the probability that each variant is the best via Monte Carlo.

    Draws samples from each variant's posterior and counts how often each
    variant has the highest value.

    Args:
        posteriors: Dict mapping variant name to its posterior distribution.
        n_simulations: Number of Monte Carlo draws. Default 100,000.
        random_seed: Random seed for reproducibility. Default 42.

    Returns:
        Dict mapping variant name to its probability of being the best.
    """
    # TODO: Set random seed
    # TODO: Draw n_simulations samples from each posterior
    #   - BetaPosterior: use np.random.beta(alpha, beta, size=n)
    #   - NIG: draw sigma^2 from InverseGamma, then mu from Normal
    # TODO: For each simulation, find the variant with the highest draw
    # TODO: Count wins per variant and normalize to probabilities
    # TODO: Return dict of probabilities
    raise NotImplementedError("Probability of being best not yet implemented")


def expected_loss(
    posteriors: Dict[str, BetaPosterior | NormalInverseGammaPosterior],
    n_simulations: int = 100_000,
    random_seed: int = 42,
) -> Dict[str, float]:
    """Compute the expected loss for each variant via Monte Carlo.

    The expected loss of choosing variant k is E[max(theta_j - theta_k, 0)]
    over all other variants j.

    Args:
        posteriors: Dict mapping variant name to its posterior distribution.
        n_simulations: Number of Monte Carlo draws. Default 100,000.
        random_seed: Random seed for reproducibility. Default 42.

    Returns:
        Dict mapping variant name to its expected loss.
    """
    # TODO: Set random seed
    # TODO: Draw samples from each posterior (reuse sampling logic)
    # TODO: For each variant k, compute:
    #   loss_k = mean(max(max_other - sample_k, 0))
    #   where max_other = max of samples from all variants except k
    # TODO: Return dict of expected losses
    raise NotImplementedError("Expected loss computation not yet implemented")


def compute_lift_distribution(
    control_posterior: BetaPosterior | NormalInverseGammaPosterior,
    treatment_posterior: BetaPosterior | NormalInverseGammaPosterior,
    n_simulations: int = 100_000,
    random_seed: int = 42,
) -> Dict[str, float]:
    """Compute summary statistics for the treatment lift distribution.

    Lift = (treatment - control) / control.

    Args:
        control_posterior: Posterior distribution for the control variant.
        treatment_posterior: Posterior distribution for the treatment variant.
        n_simulations: Number of Monte Carlo draws. Default 100,000.
        random_seed: Random seed for reproducibility. Default 42.

    Returns:
        Dict with keys: mean, median, std, p5, p25, p75, p95 of the lift.
    """
    # TODO: Draw samples from both posteriors
    # TODO: Compute lift samples: (treatment_samples - control_samples) / control_samples
    # TODO: Handle division by zero (control_samples near 0)
    # TODO: Return summary statistics dict
    raise NotImplementedError("Lift distribution computation not yet implemented")


def run_bayesian_analysis(
    experiment_data: Dict[str, Dict[str, np.ndarray]],
    metric_types: Dict[str, str],
    priors: Optional[Dict[str, Dict]] = None,
    n_simulations: int = 100_000,
    random_seed: int = 42,
) -> List[BayesianResult]:
    """Run the full Bayesian analysis pipeline on an experiment dataset.

    Args:
        experiment_data: Nested dict mapping metric_name -> variant_name -> values.
        metric_types: Dict mapping metric_name to type ("proportion" or "continuous").
        priors: Optional dict mapping metric_name to prior parameters.
            If None, default weakly informative priors are used.
        n_simulations: Number of Monte Carlo simulations. Default 100,000.
        random_seed: Random seed for reproducibility. Default 42.

    Returns:
        List of BayesianResult objects, one per metric.
    """
    # TODO: Iterate over metrics
    # TODO: Select prior model based on metric_types
    # TODO: Compute posteriors for each variant
    # TODO: Compute probability of being best
    # TODO: Compute expected loss
    # TODO: Compute lift distribution (treatment vs control)
    # TODO: Compute risk/reward (expected upside and downside)
    # TODO: Assemble and return BayesianResult list
    raise NotImplementedError("Full Bayesian analysis pipeline not yet implemented")
