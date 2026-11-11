"""
Synthesizer Module for Weekly Finance & Agentic AI Intelligence Digest.

Uses LLM (Google Gemini API / OpenAI API) or domain-specific fallback heuristics to analyze,
rank, and summarize top financial AI developments into an executive weekly briefing.
"""

from dataclasses import dataclass, field
import json
import logging
import os
import re
from typing import List, Dict, Optional, Any

try:
    from src.fetcher import NewsItem
except ImportError:
    from fetcher import NewsItem

logger = logging.getLogger("FinanceSynthesizer")


@dataclass
class StoryBrief:
    headline: str
    url: str
    source: str
    tag: str  # Institutional Deployment, Agentic AI & Automation, Quant & Trading, FinTech & Payments, RegTech & Compliance, Applied Research
    summary: str  # 2-3 sentence technical & strategic summary
    key_takeaway: str = ""  # 1 punchy bullet for fast executive skimming
    original_title: str = ""


@dataclass
class StrategicSpotlight:
    title: str
    institution: str
    theme: str
    analysis: str
    url: str


@dataclass
class WeeklyDigestContent:
    date_str: str
    macro_overview: str  # 3-sentence executive macro overview
    top_breakthroughs: List[StoryBrief] = field(default_factory=list)
    notable_initiatives: List[StoryBrief] = field(default_factory=list)
    spotlight: Optional[StrategicSpotlight] = None
    total_sources_scanned: int = 0
    total_items_ingested: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date_str": self.date_str,
            "macro_overview": self.macro_overview,
            "spotlight": self.spotlight.__dict__ if self.spotlight else None,
            "top_breakthroughs": [b.__dict__ for b in self.top_breakthroughs],
            "notable_initiatives": [n.__dict__ for n in self.notable_initiatives],
            "total_sources_scanned": self.total_sources_scanned,
            "total_items_ingested": self.total_items_ingested,
        }


class FinanceNewsSynthesizer:
    """Ranks, filters, and generates high-signal financial AI summaries."""

    ALLOWED_TAGS = [
        "Institutional Deployment",
        "Agentic AI & Automation",
        "Quant & Trading",
        "FinTech & Payments",
        "RegTech & Compliance",
        "Applied Research",
    ]

    def __init__(self, max_stories: int = 10):
        self.max_stories = max_stories
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def synthesize(self, items: List[NewsItem], date_str: str) -> WeeklyDigestContent:
        """Processes raw news items and returns a formatted WeeklyDigestContent."""
        if not items:
            return WeeklyDigestContent(
                date_str=date_str,
                macro_overview="No major financial AI developments detected across monitored feeds during the past 7-day ingestion cycle.",
                top_breakthroughs=[],
                notable_initiatives=[],
                total_sources_scanned=0,
                total_items_ingested=0,
            )

        # Attempt Gemini API synthesis
        if self.gemini_key and self.gemini_key.strip() and self.gemini_key != "your_gemini_api_key_here":
            try:
                return self._synthesize_with_gemini(items, date_str)
            except Exception as e:
                logger.error(f"Gemini API synthesis failed ({e}). Falling back to alternative engines.")

        # Attempt OpenAI API synthesis
        if self.openai_key and self.openai_key.strip() and self.openai_key != "your_openai_api_key_here":
            try:
                return self._synthesize_with_openai(items, date_str)
            except Exception as e:
                logger.error(f"OpenAI API synthesis failed ({e}). Falling back to rule-based engine.")

        # Fallback heuristic synthesizer
        logger.info("Using Financial Heuristic Fallback Synthesizer.")
        return self._synthesize_fallback(items, date_str)

    def _synthesize_with_gemini(self, items: List[NewsItem], date_str: str) -> WeeklyDigestContent:
        """Synthesizes weekly briefing using google-genai SDK."""
        from google import genai
        from google.genai import types

        logger.info("Synthesizing weekly finance briefing via Google Gemini API...")
        client = genai.Client(api_key=self.gemini_key)

        # Select candidate items for prompt context (up to 40 items)
        candidate_items = items[:40]
        items_payload = []
        for i, item in enumerate(candidate_items, 1):
            items_payload.append({
                "id": i,
                "title": item.title,
                "source": item.source,
                "url": item.url,
                "tag_hint": item.tags[0] if item.tags else "General",
                "snippet": item.raw_summary[:350],
            })

        system_instruction = (
            "You are a Principal Financial Technology Analyst, Quantitative AI Strategist, and Enterprise AI Architect. "
            "Your audience consists of Chief Investment Officers, Head of Quant Trading, FinTech Founders, and Banking Tech Leaders. "
            "Analyze the weekly developments in Artificial Intelligence and Agentic AI within the global financial sector. "
            "Highlight real implementations, autonomous agent architectures (tool-calling, RAG, multi-agent frameworks, audit logging), "
            "quantitative models, regulatory compliance, and business ROI. Avoid generic tech hype or promotional PR language."
        )

        prompt = f"""Review the following recent developments in Finance and Agentic AI from the past 7 days.
Select the top {self.max_stories} most impactful stories and organize them into an executive intelligence briefing.

Categorize each story using strictly one of these tags:
- 'Institutional Deployment' (Tier-1 banks, asset managers, hedge funds deploying AI)
- 'Agentic AI & Automation' (Autonomous multi-agent workflows, tool use, automated research/audits)
- 'Quant & Trading' (Algorithmic trading, alpha generation, financial time series, sentiment models)
- 'FinTech & Payments' (Neobanks, lending platforms, payment rails, real-time fraud)
- 'RegTech & Compliance' (AI governance, SEC/FINRA/Fed/ECB oversight, KYC/AML, explainability)
- 'Applied Research' (Academic & quant papers on econometric LLMs, financial datasets)

Output a single JSON object strictly matching this schema:
{{
  "macro_overview": "A 3-sentence executive summary analyzing the macro trends of the week in finance AI. Focus on where capital and engineering talent are concentrating.",
  "spotlight": {{
    "title": "Title of the single most significant institutional case study or regulatory shift this week",
    "institution": "Organization / Bank / FinTech involved",
    "theme": "Core theme (e.g., Autonomous Compliance Agents or Algorithmic Alpha Engine)",
    "analysis": "2-3 sentences providing in-depth analysis of the technical implementation and its competitive implications.",
    "url": "Original URL"
  }},
  "top_breakthroughs": [
    {{
      "id": 1,
      "headline": "Punchy, executive headline in active voice",
      "url": "original_url",
      "source": "source_name",
      "tag": "One of the 6 allowed tags",
      "summary": "2-3 sentence explanation: What was implemented technically, how it operates in production, and why it matters to the financial industry.",
      "key_takeaway": "One short, high-impact bullet sentence."
    }}
  ],
  "notable_initiatives": [
    {{
      "id": 2,
      "headline": "Concise initiative or release headline",
      "url": "original_url",
      "source": "source_name",
      "tag": "One of the 6 allowed tags",
      "summary": "1-2 sentence quick overview of the launch or research finding.",
      "key_takeaway": "Key takeaway sentence."
    }}
  ]
}}

Raw Ingested Finance News Items:
{json.dumps(items_payload, indent=2)}
"""

        response = None
        # Try resilient Gemini models
        for model_name in ["gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]:
            try:
                logger.info(f"Submitting briefing prompt to model: {model_name}...")
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.2,
                    ),
                )
                if resp and resp.text:
                    response = resp
                    break
            except Exception as e:
                logger.warning(f"Gemini model {model_name} invocation failed: {e}. Trying fallback model...")
                continue

        if not response or not response.text:
            raise RuntimeError("All Gemini generation attempts failed.")

        data = json.loads(response.text)

        # Parse spotlight
        spotlight = None
        sp_data = data.get("spotlight")
        if sp_data and isinstance(sp_data, dict):
            spotlight = StrategicSpotlight(
                title=sp_data.get("title", ""),
                institution=sp_data.get("institution", ""),
                theme=sp_data.get("theme", ""),
                analysis=sp_data.get("analysis", ""),
                url=sp_data.get("url", ""),
            )

        # Parse top breakthroughs
        top_breakthroughs = []
        for b in data.get("top_breakthroughs", []):
            tag = b.get("tag", "Institutional Deployment")
            if tag not in self.ALLOWED_TAGS:
                tag = "Institutional Deployment"
            top_breakthroughs.append(
                StoryBrief(
                    headline=b.get("headline", ""),
                    url=b.get("url", ""),
                    source=b.get("source", ""),
                    tag=tag,
                    summary=b.get("summary", ""),
                    key_takeaway=b.get("key_takeaway", ""),
                )
            )

        # Parse notable initiatives
        notable_initiatives = []
        for n in data.get("notable_initiatives", []):
            tag = n.get("tag", "FinTech & Payments")
            if tag not in self.ALLOWED_TAGS:
                tag = "FinTech & Payments"
            notable_initiatives.append(
                StoryBrief(
                    headline=n.get("headline", ""),
                    url=n.get("url", ""),
                    source=n.get("source", ""),
                    tag=tag,
                    summary=n.get("summary", ""),
                    key_takeaway=n.get("key_takeaway", ""),
                )
            )

        return WeeklyDigestContent(
            date_str=date_str,
            macro_overview=data.get("macro_overview", ""),
            spotlight=spotlight,
            top_breakthroughs=top_breakthroughs,
            notable_initiatives=notable_initiatives,
            total_sources_scanned=len(set(item.source for item in items)),
            total_items_ingested=len(items),
        )

    def _synthesize_with_openai(self, items: List[NewsItem], date_str: str) -> WeeklyDigestContent:
        """Synthesizes weekly briefing using OpenAI chat completion API."""
        import requests

        logger.info("Synthesizing weekly briefing via OpenAI API...")
        candidate_items = items[:35]
        items_payload = [
            {
                "id": i,
                "title": item.title,
                "source": item.source,
                "url": item.url,
                "snippet": item.raw_summary[:350],
            }
            for i, item in enumerate(candidate_items, 1)
        ]

        system_prompt = (
            "You are a quantitative financial technology analyst. Return clean, strictly formatted JSON "
            "with keys: macro_overview, spotlight, top_breakthroughs, notable_initiatives."
        )
        user_prompt = f"""Synthesize top {self.max_stories} stories from the past 7 days into an executive finance briefing.
Allowed tags: Institutional Deployment, Agentic AI & Automation, Quant & Trading, FinTech & Payments, RegTech & Compliance, Applied Research.

Items:
{json.dumps(items_payload)}
"""

        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "content", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            },
            timeout=35,
        )

        data = json.loads(resp.json()["choices"][0]["message"]["content"])
        spotlight = None
        if data.get("spotlight"):
            spotlight = StrategicSpotlight(**data["spotlight"])

        return WeeklyDigestContent(
            date_str=date_str,
            macro_overview=data.get("macro_overview", ""),
            spotlight=spotlight,
            top_breakthroughs=[StoryBrief(**b) for b in data.get("top_breakthroughs", [])],
            notable_initiatives=[StoryBrief(**n) for n in data.get("notable_initiatives", [])],
            total_sources_scanned=len(set(item.source for item in items)),
            total_items_ingested=len(items),
        )

    def _synthesize_fallback(self, items: List[NewsItem], date_str: str) -> WeeklyDigestContent:
        """Domain-tailored heuristic fallback when LLM API keys are not provided."""
        logger.info("Running domain-tailored heuristic fallback synthesizer...")

        # Categorize by keyword patterns
        agentic_items = []
        institutional_items = []
        quant_items = []
        fintech_items = []
        research_items = []

        for item in items:
            lower_text = f"{item.title.lower()} {item.raw_summary.lower()}"
            if any(k in lower_text for k in ["agent", "agentic", "autonomous", "workflow", "multi-agent", "action model"]):
                agentic_items.append(item)
            elif any(k in lower_text for k in ["jpmorgan", "goldman", "morgan stanley", "citi", "bank", "barclays", "wells fargo", "ubs"]):
                institutional_items.append(item)
            elif any(k in lower_text for k in ["trading", "quant", "algorithmic", "hedge fund", "alpha", "market maker"]):
                quant_items.append(item)
            elif any(k in lower_text for k in ["arxiv", "paper", "research", "benchmark", "dataset"]):
                research_items.append(item)
            else:
                fintech_items.append(item)

        selected = (agentic_items[:3] + institutional_items[:3] + quant_items[:2] + fintech_items[:2] + research_items[:2])
        if len(selected) < self.max_stories:
            remaining = [item for item in items if item not in selected]
            selected.extend(remaining[: self.max_stories - len(selected)])

        selected = selected[: self.max_stories]

        top_breakthroughs: List[StoryBrief] = []
        for item in selected:
            # Tag determination
            tag = "Institutional Deployment"
            lower = item.title.lower()
            if any(k in lower for k in ["agent", "autonomous", "copilot"]):
                tag = "Agentic AI & Automation"
            elif any(k in lower for k in ["quant", "trading", "hedge", "stock", "market"]):
                tag = "Quant & Trading"
            elif any(k in lower for k in ["compliance", "regtech", "sec", "fraud", "aml", "kyc"]):
                tag = "RegTech & Compliance"
            elif "ArXiv" in item.source or any(k in lower for k in ["paper", "study", "research"]):
                tag = "Applied Research"
            elif any(k in lower for k in ["pay", "payment", "card", "lending", "neobank"]):
                tag = "FinTech & Payments"

            summary = item.raw_summary.strip()
            if len(summary) > 220:
                summary = summary[:217] + "..."
            if not summary:
                summary = f"Strategic update from {item.source} highlighting {item.title}."

            top_breakthroughs.append(
                StoryBrief(
                    headline=item.title,
                    url=item.url,
                    source=item.source,
                    tag=tag,
                    summary=f"Analysis from {item.source}: {summary}",
                    key_takeaway="Key operational deployment in financial AI infrastructure.",
                    original_title=item.title,
                )
            )

        sources_count = len(set(item.source for item in items))
        macro = (
            f"Over the past 7 days, financial institutions and fintechs continued aggressively migrating from passive "
            f"analytical copilots toward autonomous agentic workflows. Focus remains centered on automated risk auditing, "
            f"document reconciliation, and multi-agent systems for quantitative research across {sources_count} monitored feeds."
        )

        spotlight = None
        if top_breakthroughs:
            first = top_breakthroughs[0]
            spotlight = StrategicSpotlight(
                title=first.headline,
                institution=first.source,
                theme="Enterprise Agentic Implementation",
                analysis=first.summary,
                url=first.url,
            )

        return WeeklyDigestContent(
            date_str=date_str,
            macro_overview=macro,
            spotlight=spotlight,
            top_breakthroughs=top_breakthroughs,
            notable_initiatives=[],
            total_sources_scanned=sources_count,
            total_items_ingested=len(items),
        )


if __name__ == "__main__":
    from datetime import datetime
    try:
        from src.fetcher import FinanceNewsFetcher
    except ImportError:
        from fetcher import FinanceNewsFetcher

    fetcher = FinanceNewsFetcher(hours_lookback=168)
    items = fetcher.fetch_all()

    synthesizer = FinanceNewsSynthesizer(max_stories=8)
    date_str = datetime.now().strftime("%B %d, %Y")
    digest = synthesizer.synthesize(items, date_str)

    print("\n=== SYNTHESIZED WEEKLY FINANCE DIGEST ===")
    print(f"Date: {digest.date_str}")
    print(f"Macro Overview: {digest.macro_overview}\n")
    if digest.spotlight:
        print(f"Spotlight: {digest.spotlight.title} ({digest.spotlight.institution})")
        print(f"Analysis: {digest.spotlight.analysis}\n")
    for b in digest.top_breakthroughs:
        print(f"[{b.tag}] {b.headline}")
        print(f"Source: {b.source} | URL: {b.url}")
        print(f"Summary: {b.summary}\n")

