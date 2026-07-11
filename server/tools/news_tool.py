import xml.etree.ElementTree as ET
import httpx
import re
from typing import List, Dict, Any

# Phrases that are characteristic of prompt-injection payloads.
# These are matched case-insensitively and replaced with [FILTERED].
_INJECTION_PATTERNS = re.compile(
    r"\b("
    r"ignore[\s\S]{0,20}(previous|above|all|prior)|"
    r"forget[\s\S]{0,20}(previous|above|all|prior)|"
    r"disregard[\s\S]{0,20}(previous|above|all|prior)|"
    r"override[\s\S]{0,20}(instruction|prompt|rule)|"
    r"new\s+instruction|"
    r"system\s*:|"
    r"you\s+must\s+(now|instead)|"
    r"do\s+not\s+follow|"
    r"don'?t\s+follow|"
    r"\[INST\]|"
    r"<\|"
    r")\s*",
    re.IGNORECASE,
)

_MAX_TITLE_LEN = 200
_MAX_SUMMARY_LEN = 500


class NewsTool:
    def __init__(self):
        self.rss_url = "https://news.google.com/rss/search?q=SRAG+OR+influenza+OR+covid+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_external_text(text: str, max_length: int = _MAX_TITLE_LEN) -> str:
        """
        Sanitises a string sourced from an external (untrusted) RSS feed before it is
        incorporated into an LLM prompt.

        Defence layers applied (in order):
        1. Strip leading/trailing whitespace.
        2. Remove embedded newlines — prevents multi-line prompt manipulation.
        3. Replace known prompt-injection trigger phrases with [FILTERED].
        4. Truncate to `max_length` to prevent payload smuggling via very long strings.
        """
        if not text:
            return ""
        # 1. Strip whitespace
        text = text.strip()
        # 2. Collapse newlines to spaces to prevent multi-line payloads
        text = re.sub(r"[\r\n]+", " ", text)
        # 3. Neutralise injection trigger phrases
        text = _INJECTION_PATTERNS.sub("[FILTERED] ", text)
        # 4. Enforce maximum length
        if len(text) > max_length:
            text = text[:max_length].rstrip() + "…"
        return text

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_news(self, query: str = "SRAG") -> Dict[str, Any]:
        """
        Retrieves recent news about SRAG or respiratory infections.

        SECURITY: All text fields returned from the RSS feed are sanitised by
        `_sanitize_external_text()` before leaving this method, to prevent
        prompt-injection payloads from reaching the LLM context.

        Returns:
            Dict containing success status and list of news dicts:
            {
                "success": true,
                "news": [{"title": ..., "date": ..., "url": ..., "summary": ...}]
            }
        """
        try:
            # Query customizer for RSS search
            search_query = f"{query} Brasil"
            url = f"https://news.google.com/rss/search?q={search_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

            root = ET.fromstring(response.content)
            items = root.findall(".//item")

            news_list = []
            # Take top 5 news articles
            for item in items[:5]:
                raw_title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                raw_source = item.find("source").text if item.find("source") is not None else "Google News"

                # Clean up title: remove " - SourceName" suffix, then sanitise
                clean_title = re.sub(r'\s+-\s+.*$', '', raw_title)
                safe_title = self._sanitize_external_text(clean_title, max_length=_MAX_TITLE_LEN)
                safe_source = self._sanitize_external_text(raw_source, max_length=100)
                safe_summary = self._sanitize_external_text(
                    f"Recent coverage by {safe_source} reporting on '{safe_title}' "
                    f"regarding respiratory concerns in Brazil.",
                    max_length=_MAX_SUMMARY_LEN,
                )

                news_list.append({
                    "title": safe_title,
                    "date": pub_date,
                    "url": link,
                    "summary": safe_summary,
                })

            return {
                "success": True,
                "news": news_list
            }

        except Exception as e:
            # Do NOT fabricate news — return a structured error so the agent can handle it transparently
            print(f"News RSS fetch failed: {str(e)}")
            return {
                "success": False,
                "reason": f"Could not retrieve news: {str(e)}",
                "news": []
            }
