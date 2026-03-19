---
name: compliance-review
description: >
  Use when the user mentions compliance review, regulatory check, SEC compliance,
  FINRA compliance, FCA compliance, marketing compliance, disclosure check, disclaimer,
  performance presentation, testimonial compliance, endorsement compliance, fair and
  balanced, risk disclosure, past performance disclaimer, GIPS, investment advertisement,
  financial promotion, advertising review, regulatory filing, or archival requirements.
  ALWAYS trigger automatically when any other skill produces customer-facing content in a
  workspace tagged as financial services. Also trigger on 'is this compliant' or 'check
  this for regulatory issues.'
---

# Compliance-Aware Content Review

Automated regulatory content screening for SEC, FINRA, and FCA marketing compliance.

> **ADVISORY NOTICE:** This skill provides an advisory first-pass review only. It does
> NOT constitute compliance certification, legal advice, or regulatory approval. All
> findings require confirmation by a qualified human compliance officer before any
> content is distributed. Never treat output from this skill as a final compliance
> determination.

## Objective

Automate first-pass regulatory compliance review of marketing content for financial
services organizations. Check content against SEC Marketing Rule 206(4)-1, FINRA
Rule 2210, and FCA financial promotions requirements. Flag potential violations, insert
required disclosures, validate performance presentation requirements, and maintain
archival records. Function as a mandatory gate that all content-producing skills must
pass through before distribution in financial services contexts.

This skill is a terminal gate: it does not modify content unilaterally. It flags issues
and suggests remediation, preserving the human compliance officer's final authority.

## SEC Marketing Rule 206(4)-1 Screening

The SEC Marketing Rule applies to registered investment advisers. The skill screens
content against the seven general prohibitions:

1. **Untrue statements of material fact** -- Flag any factual claim that is not
   substantiated by source data in the workspace.
2. **Unsubstantiated material claims** -- Require that every material statement of fact
   has a traceable data source or citation.
3. **Untrue or misleading implications** -- Detect language that could create a false
   impression even if technically accurate in isolation.
4. **Failure to disclose material facts** -- Check that content mentioning performance
   or investment characteristics includes all material context.
5. **Misleading use of cherry-picked performance** -- Detect selective time-period
   presentation; require all standard reporting periods.
6. **Statements materially misleading to the intended audience** -- Consider whether
   claims appropriate for institutional investors appear in retail-facing content.
7. **Otherwise materially misleading statements** -- Catch-all for content that
   creates unjustified expectations.

### Performance Presentation Standards

- Gross and net performance must receive equal prominence when both are shown.
- Performance must include 1-year, 5-year, and 10-year (or since-inception) periods.
- Benchmarks must accompany any performance comparison.
- Hypothetical and back-tested performance requires specific disclosures.
- Extracted performance must include total portfolio results.

### Testimonial and Endorsement Requirements

- Cash and non-cash compensation must be disclosed.
- Material conflicts of interest must be stated.
- Content from current clients must note that client status exists.
- Testimonials must not be misleading when read in context.

## FINRA Rule 2210 Compliance

FINRA Rule 2210 governs communications with the public by broker-dealers.

### Content Classification

The skill classifies each piece of content into one of three FINRA categories:

| Category | Definition | Filing Requirement |
|---|---|---|
| **Institutional** | Distributed only to institutional investors (>$50M AUM) | Post-use filing within 10 business days |
| **Retail** | Any communication available to 25+ retail investors in 30 days | Pre-use filing for new members; post-use for established |
| **Correspondence** | Written to 25 or fewer retail investors in 30 days | Spot-check supervision |

### Fair and Balanced Standard

- Every statement of benefit must be balanced with associated risks.
- Claims must not exaggerate potential returns or minimize risks.
- Projections and forecasts are prohibited for retail communications.
- Comparisons to other products must be fair and substantiated.
- Past performance language must include "past performance does not guarantee future
  results" or equivalent approved language.

### Filing Requirements

Flag content requiring FINRA pre-filing:
- Communications from firms in their first year of membership.
- Options-related content (pre-use filing with OCC).
- CMO/structured product communications.
- Leveraged and inverse ETF materials.
- Communications about registered investment companies (mutual funds, ETFs).

## FCA Financial Promotions Compliance

The FCA regulates financial promotions in the United Kingdom under FSMA 2000 s.21.

### Clear, Fair, and Not Misleading Standard

All financial promotions must be:
- **Clear** -- Key information is prominent and understandable to the target audience.
- **Fair** -- Benefits and risks receive balanced treatment; no cherry-picking.
- **Not misleading** -- Nothing that could create a false or deceptive impression.

### Risk Warning Requirements

- Specific risk warnings for each product category (UCITS, AIFs, structured deposits).
- Capital-at-risk warning when applicable.
- Past performance warning: "Past performance is not a reliable indicator of future
  results."
- Complexity warnings for products classified as complex under MiFID II.

### Target Market Assessment

- Content must be appropriate for the identified target market.
- Retail investor materials have stricter clarity requirements than professional.
- High-risk investment warnings required where applicable (as of FCA PS22/10).

## Disclosure Management

### Disclosure Insertion Logic

Based on content classification, the skill determines which disclosures are required
and suggests insertion points:

| Content Type | Required Disclosures |
|---|---|
| Performance claims | Past performance disclaimer, gross/net disclosure, benchmark citation |
| Testimonials | Compensation disclosure, conflict of interest, client status |
| Hypothetical results | Hypothetical performance disclaimer, methodology description |
| Third-party ratings | Rating methodology disclosure, date of rating, compensation |
| Fee references | Complete fee schedule reference, expense ratio if applicable |
| Risk statements | Specific risk factors, capital-at-risk warning |

### Disclosure Validation

- Verify all required disclosures are present for the content type.
- Check disclosure placement: must be prominent, not buried in footnotes for key items.
- Validate disclosure language matches firm-approved templates.
- Confirm disclosures are current (date-sensitive disclaimers updated).

### Customization

Disclosure templates support per-firm customization. Each organization maintains its
own approved disclosure language in `references/disclosure_templates.md`. The skill
uses these templates as the basis for insertion and validation, falling back to
regulatory-standard language if firm-specific templates are not configured.

## Content Classification

The skill classifies incoming content along multiple dimensions:

1. **Regulatory jurisdiction** -- SEC (US-registered advisers), FINRA (US
   broker-dealers), FCA (UK), or multiple.
2. **Audience type** -- Institutional vs. retail vs. correspondence.
3. **Content type** -- Performance, testimonial, educational, promotional, commentary.
4. **Risk level** -- High (definite violation), Medium (likely issue), Low (potential
   concern), Info (best-practice suggestion).
5. **Filing requirement** -- Pre-use filing, post-use filing, or supervision only.

## Archival Tagging

All reviewed content is tagged with archival metadata for regulatory retention:

- **Content ID** -- Unique identifier for the reviewed piece.
- **Review timestamp** -- ISO 8601 datetime of the review.
- **Reviewer** -- "automated-first-pass" (always; human reviewer added later).
- **Retention period** -- Per SEC Rule 17a-4 and FINRA requirements (typically 3-6
  years depending on content type).
- **WORM flag** -- Whether the content must be stored in Write-Once-Read-Many format.
- **Filing status** -- Whether FINRA filing is required and current status.
- **Classification** -- The content classification determined during review.

See `references/archival_requirements.md` for retention schedules.

## Input / Output Data Contracts

### Inputs

| Source | Description |
|---|---|
| `workspace/reports/*.html` or `*.docx` | Content produced by other skills for distribution |
| `workspace/analysis/mmm_executive_summary.html` | Attribution reports with performance claims |
| `workspace/analysis/experiment_results.json` | Experiment results used in marketing claims |
| `references/compliance_rules/` | Regulatory rule database (SEC, FINRA, FCA) |

### Outputs

| File | Description |
|---|---|
| `workspace/compliance/review_report.json` | Issue-by-issue review with severity, rule citation, remediation |
| `workspace/compliance/compliant_content.html` | Content with required disclosures inserted |
| `workspace/compliance/archival_manifest.json` | Content tagged for regulatory archival with retention metadata |
| `workspace/compliance/review_log.json` | Immutable audit trail of all reviews performed |

### Output Schema: review_report.json

```json
{
  "review_id": "string (UUID)",
  "review_timestamp": "string (ISO 8601)",
  "content_source": "string (file path)",
  "overall_status": "PASS | FAIL | WARNING",
  "advisory_notice": "This is an advisory first-pass review, not compliance certification.",
  "issues": [
    {
      "issue_id": "string",
      "severity": "HIGH | MEDIUM | LOW | INFO",
      "category": "SEC | FINRA | FCA | DISCLOSURE | ARCHIVAL",
      "rule_citation": "string (e.g., 'SEC Rule 206(4)-1(a)(2)')",
      "description": "string",
      "location": "string (content location reference)",
      "remediation": "string (suggested fix)",
      "requires_human_review": true
    }
  ],
  "disclosures_required": ["string"],
  "disclosures_present": ["string"],
  "disclosures_missing": ["string"],
  "classification": {
    "jurisdiction": ["SEC", "FINRA", "FCA"],
    "audience": "INSTITUTIONAL | RETAIL | CORRESPONDENCE",
    "content_type": "string",
    "filing_required": "PRE_USE | POST_USE | NONE"
  },
  "archival_metadata": {
    "retention_period_years": 0,
    "worm_required": true,
    "content_hash": "string (SHA-256)"
  }
}
```

## Cross-Skill Integration

Compliance review is the mandatory terminal gate in financial services workflows.
Every skill that produces customer-facing content must route through compliance-review
before distribution when the workspace is tagged as financial services:

- **reporting** -- Executive summaries with performance claims.
- **email-analytics** -- Email content referencing investment returns or products.
- **paid-media** -- Ad copy for financial products or services.
- **seo-content** -- Website content making investment-related claims.
- **social-analytics** -- Social media posts about financial performance.
- **attribution-analysis** -- Reports containing performance data that may be used
  in marketing.

The skill reads content from other skills' output directories and writes compliance
review results to `workspace/compliance/`. It does not block other skills from
running; it operates as a post-production gate.

## Development Guidelines

1. **Advisory only** -- Compliance review must function as an advisory tool, not an
   automated approval system. Always recommend human compliance officer final review.
   Every output must state: "This is an advisory first-pass review, not compliance
   certification."

2. **Versioned rule database** -- The rule database in `references/` must be versioned
   and updatable without modifying core skill scripts. Reference files carry their own
   effective dates and version numbers.

3. **Precision over recall** -- False positive rate must be below 30% to maintain
   reviewer trust. Prioritize precision over recall for low-severity issues. High-
   severity violations (superlatives, guarantees) should have near-100% recall.

4. **Firm-customizable disclosures** -- Disclosure templates must support customization
   per firm. Each organization has specific approved language that overrides defaults.

5. **Severity distinction** -- Clearly distinguish between definite violations
   (superlative claims, guarantees) and potential issues requiring judgment (tone,
   emphasis). Use HIGH severity only for clear rule violations.

6. **Archival compatibility** -- Archival tagging must produce metadata compatible with
   common compliance archival systems (Smarsh, Global Relay, Bloomberg Vault).

7. **No authoritative claims** -- Never claim compliance decisions are authoritative.
   Always label output as "first-pass review" requiring human confirmation.

8. **Audit trail** -- The review log must be append-only and immutable once written.
   Each entry includes timestamp, content hash, findings, and reviewer identity.

9. **Modular scripts** -- Scripts handle deterministic computation (pattern matching,
   validation, insertion, tagging). The LLM handles nuanced interpretation and
   contextual judgment. Keep these responsibilities clearly separated.

10. **Fail-safe defaults** -- When in doubt, flag for human review rather than passing
    content silently. It is better to over-flag than to miss a genuine violation.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/content_scanner.py` | Rule-based scanning for regulatory violations using keyword and pattern matching |
| `scripts/performance_validator.py` | Validate performance presentation: gross/net balance, time period completeness, benchmark inclusion |
| `scripts/disclosure_inserter.py` | Insert required disclosures based on content type classification |
| `scripts/archival_tagger.py` | Tag content with archival metadata per SEC 17a-4 and FINRA requirements |

## Reference Files

| File | Purpose |
|---|---|
| `references/sec_marketing_rule.md` | SEC Rule 206(4)-1 requirements, general prohibitions, performance standards |
| `references/finra_rule_2210.md` | FINRA communications standards, filing requirements, content classifications |
| `references/fca_financial_promotions.md` | FCA clear/fair/not misleading standard, risk warning requirements |
| `references/disclosure_templates.md` | Standard disclosure language for performance, risk, fees, testimonials |
| `references/archival_requirements.md` | SEC Rule 17a-4, FINRA retention rules, WORM format requirements |
