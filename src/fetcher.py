"""
Fetcher Module for Weekly Finance & Agentic AI Intelligence Digest.

Scrapes, parses, filters, and deduplicates news, case studies, institutional releases,
and quantitative research across financial services, banking, fintech, and capital markets.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import logging
import re
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

import bs4
import feedparser
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FinanceFetcher")


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    published_at: datetime
    raw_summary: str = ""
    authors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "raw_summary": self.raw_summary,
            "authors": self.authors,
            "tags": self.tags,
        }


class FinanceNewsFetcher:
    """Fetches and deduplicates Finance & Agentic AI news across specialized feeds and research sources."""

    # 1. Specialized Financial & FinTech RSS feeds
    FINANCE_RSS_SOURCES = [
        {
            "name": "Finextra AI & ML",
            "url": "https://www.finextra.com/rss/topic.aspx?topic=artificialintelligence",
            "category": "FinTech & Banking",
        },
        {
            "name": "Fintech Futures AI",
            "url": "https://www.fintechfutures.com/category/tech/ai/feed/",
            "category": "FinTech & Banking",
        },
        {
            "name": "PYMNTS AI & Payments",
            "url": "https://www.pymnts.com/category/artificial-intelligence/feed/",
            "category": "Payments & Commerce",
        },
        {
            "name": "The Financial Brand",
            "url": "https://thefinancialbrand.com/feed/",
            "category": "Retail Banking & CX",
        },
        {
            "name": "Banking Dive News",
            "url": "https://www.bankingdive.com/feeds/news/",
            "category": "Banking Operations",
        },
    ]

    # 2. Targeted Google News Topic Feeds for Financial AI & Agentic AI
    GOOGLE_NEWS_FEEDS = [
        {
            "name": "Google News (Agentic AI in Finance)",
            "url": "https://news.google.com/rss/search?q=%22agentic+AI%22+AND+(finance+OR+banking+OR+fintech+OR+%22hedge+fund%22+OR+trading)&hl=en-US&gl=US&ceid=US:en",
            "category": "Agentic AI & Automation",
        },
        {
            "name": "Google News (Wall Street & Institutional AI)",
            "url": "https://news.google.com/rss/search?q=(%22generative+AI%22+OR+%22AI+agents%22)+AND+(%22Wall+Street%22+OR+%22JPMorgan%22+OR+%22Goldman+Sachs%22+OR+%22Morgan+Stanley%22+OR+%22Citigroup%22+OR+%22BlackRock%22+OR+%22Bloomberg%22)&hl=en-US&gl=US&ceid=US:en",
            "category": "Institutional Deployment",
        },
        {
            "name": "Google News (Quant & Algorithmic Trading AI)",
            "url": "https://news.google.com/rss/search?q=(%22algorithmic+trading%22+OR+%22quantitative+finance%22+OR+%22hedge+fund%22+OR+%22alpha+generation%22)+AND+(%22AI%22+OR+%22LLM%22+OR+%22machine+learning%22+OR+%22agent%22)&hl=en-US&gl=US&ceid=US:en",
            "category": "Quant & Trading",
        },
        {
            "name": "Google News (RegTech, Risk & Fraud AI)",
            "url": "https://news.google.com/rss/search?q=(%22fintech%22+OR+%22regtech%22+OR+%22credit+underwriting%22+OR+%22fraud+detection%22+OR+%22anti-money+laundering%22)+AND+(%22AI%22+OR+%22agent%22+OR+%22LLM%22)&hl=en-US&gl=US&ceid=US:en",
            "category": "RegTech & Risk",
        },
    ]

    # 3. Academic research feeds
    ARXIV_SOURCES = [
        {
            "name": "ArXiv Quantitative Finance",
            "url": "http://export.arxiv.org/rss/q-fin",
            "category": "Applied Research",
            "filter_type": "ai_keywords",
        },
        {
            "name": "ArXiv cs.AI (Finance filtered)",
            "url": "http://export.arxiv.org/rss/cs.AI",
            "category": "Applied Research",
            "filter_type": "finance_keywords",
        },
    ]

    USER_AGENT = "Mozilla/5.0 (compatible; WeeklyFinanceAIBriefing/1.0; +https://github.com/weekly-finance-ai-digest)"

    # Filter keyword lists
    AI_KEYWORDS = {
        "ai", "agent", "agents", "agentic", "llm", "large language model", "neural",
        "deep learning", "transformer", "reinforcement learning", "machine learning",
        "nlp", "sentiment", "foundation model", "gpt", "generative", "rag", "diffusion"
    }

    FINANCE_KEYWORDS = {
        "finance", "financial", "banking", "bank", "trading", "stock", "portfolio",
        "credit", "fraud", "fintech", "hedge fund", "regtech", "market", "wealth",
        "asset management", "underwriting", "aml", "kyc", "investment", "bonds"
    }

    def __init__(self, hours_lookback: int = 168):
        """Initializes fetcher with a lookback window (default 168 hours = 7 days)."""
        self.hours_lookback = hours_lookback
        self.cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_lookback)

    def clean_url(self, url: str) -> str:
        """Removes tracking query parameters (utm_*, ref, etc.) and normalizes URLs."""
        if not url:
            return ""
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        clean_query = {
            k: v for k, v in query.items()
            if not k.startswith("utm_") and k not in ["ref", "source", "fbclid", "oc", "ved", "usg"]
        }
        new_query_str = urlencode(clean_query, doseq=True)
        clean_parsed = parsed._replace(query=new_query_str, fragment="")
        path = clean_parsed.path.rstrip("/")
        clean_parsed = clean_parsed._replace(path=path)
        return urlunparse(clean_parsed)

    def clean_text(self, html_or_text: str) -> str:
        """Strips HTML tags and normalizes whitespace."""
        if not html_or_text:
            return ""
        soup = bs4.BeautifulSoup(html_or_text, "html.parser")
        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def parse_entry_date(self, entry) -> datetime:
        """Extracts publication date from an RSS feed entry, defaulting to current time if absent."""
        parsed_dt = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                parsed_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                parsed_dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass

        if not parsed_dt:
            parsed_dt = datetime.now(timezone.utc)

        return parsed_dt

    def fetch_rss_feed(self, source_dict: Dict, filter_type: Optional[str] = None) -> List[NewsItem]:
        """Fetches items from a single RSS feed within the lookback window."""
        items: List[NewsItem] = []
        name = source_dict["name"]
        url = source_dict["url"]
        category = source_dict.get("category", "General")

        logger.info(f"Fetching RSS feed: {name}...")
        try:
            resp = requests.get(url, headers={"User-Agent": self.USER_AGENT}, timeout=12)
            if resp.status_code != 200:
                logger.warning(f"HTTP {resp.status_code} when fetching {name}")
                return items

            feed = feedparser.parse(resp.content)
            for entry in feed.entries:
                pub_date = self.parse_entry_date(entry)

                # Time window filtering
                if pub_date < self.cutoff_time:
                    continue

                title = self.clean_text(getattr(entry, "title", ""))
                link = self.clean_url(getattr(entry, "link", ""))
                summary = self.clean_text(getattr(entry, "summary", "") or getattr(entry, "description", ""))

                if not title or not link:
                    continue

                # Content keyword filtering for academic feeds
                combined_text = f"{title.lower()} {summary.lower()}"
                if filter_type == "ai_keywords":
                    if not any(kw in combined_text for kw in self.AI_KEYWORDS):
                        continue
                elif filter_type == "finance_keywords":
                    if not any(kw in combined_text for kw in self.FINANCE_KEYWORDS):
                        continue

                authors = []
                if hasattr(entry, "author") and entry.author:
                    authors.append(entry.author)

                items.append(
                    NewsItem(
                        title=title,
                        url=link,
                        source=name,
                        published_at=pub_date,
                        raw_summary=summary[:1000],
                        authors=authors,
                        tags=[category],
                    )
                )
        except Exception as e:
            logger.error(f"Error fetching {name}: {e}")

        logger.info(f"Fetched {len(items)} items from {name}.")
        return items

    def fetch_all_rss(self) -> List[NewsItem]:
        """Fetches all configured RSS feeds (Fintech, Google News topic feeds, ArXiv)."""
        all_items: List[NewsItem] = []

        # Standard finance feeds
        for source in self.FINANCE_RSS_SOURCES:
            all_items.extend(self.fetch_rss_feed(source))

        # Google News finance AI feeds
        for source in self.GOOGLE_NEWS_FEEDS:
            all_items.extend(self.fetch_rss_feed(source))

        # ArXiv research feeds with targeted keywords
        for source in self.ARXIV_SOURCES:
            all_items.extend(self.fetch_rss_feed(source, filter_type=source.get("filter_type")))

        return all_items

    def fetch_hacker_news_finance_ai(self, max_items: int = 40) -> List[NewsItem]:
        """Fetches top Hacker News discussions combining finance and AI/agentic themes."""
        logger.info("Fetching Hacker News discussions on Finance & Agentic AI...")
        items: List[NewsItem] = []
        url = "https://hn.algolia.com/api/v1/search_by_date"
        params = {
            "tags": "story",
            "query": "(finance OR fintech OR banking OR trading OR \"hedge fund\" OR credit OR underwriting) AND (AI OR agent OR LLM OR GPT OR Claude OR Gemini)",
            "numericFilters": f"created_at_i>{int(self.cutoff_time.timestamp())}",
            "hitsPerPage": max_items,
        }
        try:
            resp = requests.get(url, params=params, headers={"User-Agent": self.USER_AGENT}, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                for hit in data.get("hits", []):
                    title = hit.get("title", "")
                    story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                    created_at_i = hit.get("created_at_i")
                    pub_date = (
                        datetime.fromtimestamp(created_at_i, tz=timezone.utc)
                        if created_at_i
                        else datetime.now(timezone.utc)
                    )
                    points = hit.get("points", 0)

                    # Keep items with reasonable relevance or discussion
                    if points < 5 and not any(kw in title.lower() for kw in ["trading", "banking", "finance", "sec", "agent", "llm"]):
                        continue

                    items.append(
                        NewsItem(
                            title=title,
                            url=self.clean_url(story_url),
                            source="Hacker News (Finance & AI)",
                            published_at=pub_date,
                            raw_summary=f"Community discussion ({points} points, {hit.get('num_comments', 0)} comments).",
                            tags=["Community Discussion"],
                        )
                    )
        except Exception as e:
            logger.error(f"Error fetching Hacker News finance items: {e}")

        logger.info(f"Fetched {len(items)} items from Hacker News.")
        return items

    def _token_set(self, text: str) -> Set[str]:
        """Extracts normalized alphanumeric words from text excluding common stop words."""
        words = re.findall(r"\w+", text.lower())
        stopwords = {
            "a", "an", "the", "and", "or", "in", "of", "to", "for", "with", "on", "at",
            "by", "from", "is", "are", "new", "ai", "using", "how", "why", "what", "its",
            "via", "into", "over", "after", "says", "year", "years"
        }
        return {w for w in words if len(w) > 2 and w not in stopwords}

    def jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """Calculates Jaccard similarity index between two word sets."""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / float(union)

    def deduplicate(self, items: List[NewsItem], similarity_threshold: float = 0.50) -> List[NewsItem]:
        """Deduplicates news items based on normalized URLs and title token Jaccard similarity."""
        deduped: List[NewsItem] = []
        seen_urls: Set[str] = set()

        for item in items:
            clean_link = item.url
            if clean_link in seen_urls:
                continue

            item_tokens = self._token_set(item.title)
            is_duplicate = False

            for existing in deduped:
                existing_tokens = self._token_set(existing.title)
                sim = self.jaccard_similarity(item_tokens, existing_tokens)
                if sim >= similarity_threshold:
                    is_duplicate = True
                    logger.debug(f"Duplicate detected: '{item.title}' matches '{existing.title}' (sim={sim:.2f})")
                    # If current item is from an authoritative publisher or research paper, prioritize it
                    if ("Finextra" in item.source or "ArXiv" in item.source or "Dive" in item.source) and ("Google News" in existing.source):
                        existing.title = item.title
                        existing.url = item.url
                        existing.source = item.source
                        existing.tags = item.tags
                    break

            if not is_duplicate:
                seen_urls.add(clean_link)
                deduped.append(item)

        logger.info(f"Deduplicated {len(items)} items down to {len(deduped)} distinct items.")
        return deduped

    def fetch_all(self) -> List[NewsItem]:
        """Executes full weekly ingestion, combination, and deduplication pipeline."""
        raw_items = []
        raw_items.extend(self.fetch_all_rss())
        raw_items.extend(self.fetch_hacker_news_finance_ai())

        # Sort items chronologically descending
        raw_items.sort(key=lambda x: x.published_at, reverse=True)

        final_items = self.deduplicate(raw_items)
        return final_items


if __name__ == "__main__":
    fetcher = FinanceNewsFetcher(hours_lookback=168)
    results = fetcher.fetch_all()
    print(f"\nTotal weekly deduplicated items fetched: {len(results)}")
    for i, res in enumerate(results[:12], 1):
        print(f"{i}. [{res.source}] [{', '.join(res.tags)}] {res.title}")
        print(f"   URL: {res.url}")
        print(f"   Date: {res.published_at}")
        print("-" * 60)

