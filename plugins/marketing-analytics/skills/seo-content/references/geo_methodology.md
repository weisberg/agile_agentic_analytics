# Generative Engine Optimization (GEO) Methodology

Strategies for optimizing content visibility in AI-generated search results
and tracking citations across LLM-powered answer engines.

## Overview

Generative Engine Optimization (GEO) extends traditional SEO to address
AI-generated search experiences: Google AI Overviews, ChatGPT search,
Perplexity, and other LLM-powered answer engines. Unlike traditional SERP
rankings, GEO focuses on whether your content is cited, quoted, or
paraphrased in AI-generated responses.

## AI Search Landscape

### Platforms to Monitor

| Platform | Citation Behavior | Monitoring Approach |
| :------- | :---------------- | :------------------ |
| Google AI Overviews | Inline source links in AI summaries | GSC `searchAppearance` filter, manual sampling |
| ChatGPT (with search) | Footnote citations with source URLs | API query sampling, manual verification |
| Perplexity | Numbered source citations with snippets | API monitoring, brand mention tracking |
| Bing Copilot | Inline citations in conversational results | Bing Webmaster Tools, sampling |
| Gemini | Variable citation format | Manual sampling, Google integration data |

### Key Metrics

| Metric | Definition |
| :----- | :--------- |
| Citation frequency | Number of times your content is cited in AI answers for tracked queries |
| Citation accuracy | Whether cited claims correctly represent your content |
| Share of AI voice | Your citations as a percentage of all citations for a query set |
| Citation position | Whether your source appears first, second, etc. in citation lists |
| AI referral traffic | Clicks from AI-generated answers to your site |

## Content Optimization Strategies

### Structure for AI Extractability

1. **Clear, hierarchical headers.** Use descriptive H2/H3 headers that mirror
   common question patterns. AI models use headers as signals for content
   relevance.

2. **Concise answer blocks.** Place direct, factual answers in the first 1-2
   sentences after each header. AI engines prefer extracting complete, concise
   statements.

3. **Structured data (JSON-LD).** Implement FAQ, HowTo, Article, and Product
   schema markup. Structured data helps AI engines parse content semantics.

4. **Tables and lists.** Present comparative data in HTML tables and processes
   in ordered lists. These formats are more reliably extracted than prose.

5. **Authoritative sourcing.** Cite primary sources, include data points with
   dates, and reference established authorities. AI engines favor content that
   demonstrates factual authority.

### Topical Authority Building

- Create comprehensive topic clusters with a pillar page and supporting
  content that covers subtopics in depth.
- Ensure internal linking between cluster pages to signal topical
  relationships.
- Update content regularly with current data to maintain freshness signals.
- Build entity associations: consistently associate your brand with key topics
  through structured data and consistent terminology.

### E-E-A-T Signals

- **Experience:** Include first-person analysis, case studies, and original
  research.
- **Expertise:** Author bylines with credentials, about pages with
  qualifications.
- **Authoritativeness:** Backlinks from authoritative domains, brand mentions,
  industry recognition.
- **Trustworthiness:** HTTPS, privacy policy, clear editorial standards,
  factual accuracy.

## Citation Tracking Approaches

### Automated Monitoring

1. **Query sampling.** Maintain a list of priority queries (brand terms,
   product terms, key informational queries). Periodically submit these to AI
   search platforms and parse responses for citations.

2. **Referral traffic analysis.** Monitor analytics for traffic from known AI
   search domains (perplexity.ai, chat.openai.com, etc.). Track trends in AI
   referral volume.

3. **GSC search appearance data.** Filter Search Console data by
   `searchAppearance` to identify queries where your content appears in AI
   Overviews.

### Manual Audit Protocol

For queries where automated monitoring is not available:

1. Compile a list of 50-100 priority queries per month.
2. Submit each query to Google (logged out, incognito), ChatGPT, and
   Perplexity.
3. Record whether your brand/content is cited in the AI response.
4. Note citation position, accuracy, and completeness.
5. Track month-over-month changes in citation frequency.

### Competitive Citation Analysis

- Run the same query set against competitors.
- Calculate share of AI voice: your citations / total citations per query.
- Identify queries where competitors are cited but you are not (AI citation
  gap).
- Prioritize content optimization for high-value gap queries.

## Measurement Framework

### Scoring Model

For each tracked query, compute a GEO visibility score:

```
geo_score = (citation_present * 0.4) +
            (citation_position_score * 0.3) +
            (citation_accuracy * 0.2) +
            (ai_referral_click * 0.1)
```

Where:
- `citation_present`: 1 if cited, 0 if not.
- `citation_position_score`: 1.0 for first citation, 0.7 for second, 0.4 for
  third+, 0 if absent.
- `citation_accuracy`: 1 if accurate, 0.5 if partially accurate, 0 if
  inaccurate.
- `ai_referral_click`: 1 if a click-through was observed, 0 if not.

### Reporting Cadence

- **Weekly:** Track citation frequency changes for top 20 priority queries.
- **Monthly:** Full audit of 100 priority queries across all platforms.
- **Quarterly:** Competitive share of AI voice analysis and strategy review.

## Extensibility

GEO is a rapidly evolving discipline. The implementation should:

- Store platform-specific monitoring logic in separate modules so new
  platforms can be added without modifying core tracking code.
- Use a plugin architecture for citation parsers, since each AI platform has
  different citation formats.
- Version-control query lists and scoring weights so changes can be tracked
  over time.
- Log raw AI responses for audit trails and methodology refinement.
