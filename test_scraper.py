
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.scraper import scrape_text_with_bs4

async def test_scraper():
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.stackoverflow.com"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing scraper with: {url}")
        try:
            result = await scrape_text_with_bs4(url)
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                text_length = len(result.get('text', ''))
                print(f"✅ Success! Scraped {text_length} characters")
                print(f"📄 First 200 characters: {result.get('text', '')[:200]}...")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraper())