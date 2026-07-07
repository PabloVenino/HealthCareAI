import xml.etree.ElementTree as ET
import httpx
import re
from typing import List, Dict, Any

class NewsTool:
    def __init__(self):
        self.rss_url = "https://news.google.com/rss/search?q=SRAG+OR+influenza+OR+covid+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    def search_news(self, query: str = "SRAG") -> Dict[str, Any]:
        """
        Retrieves recent news about SRAG or respiratory infections.
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
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                
                # Google News RSS doesn't have a long summary in description, 
                # but we can generate a short summary snippet from the title or source
                source = item.find("source").text if item.find("source") is not None else "Google News"
                
                # Clean up title: remove " - SourceName" at the end
                clean_title = re.sub(r'\s+-\s+.*$', '', title)
                
                news_list.append({
                    "title": clean_title,
                    "date": pub_date,
                    "url": link,
                    "summary": f"Recent coverage by {source} reporting on '{clean_title}' regarding respiratory concerns in Brazil."
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
