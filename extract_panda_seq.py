import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://www.dxmwx.org"

# Fetch the chapter menu
async def fetch_menu(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Extract chapter links from the menu
def extract_chapters(html):
    soup = BeautifulSoup(html, 'html.parser')
    chapters = []
    for link in soup.select('a[href^="/read/"]'):
        chapter_title = link.text.strip()
        chapter_url = urljoin(base_url, link['href'])
        chapters.append((chapter_title, chapter_url))
    return chapters

# Fetch and parse a single chapter
async def fetch_chapter(session, url, index):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            content_div = soup.find('div', id='Lab_Contents')
            if content_div:
                chapter_text = '\n'.join(p.get_text().strip() for p in content_div.find_all('p', id=lambda x: x and x.startswith('txt_')))
                return index, chapter_text
            return index, None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return index, None

# Main function
async def main():
    menu_url = urljoin(base_url, "/chapter/57624.html")
    menu_html = await fetch_menu(menu_url)
    chapters = extract_chapters(menu_html)
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_chapter(session, url, idx) for idx, (_, url) in enumerate(chapters)]
        results = await asyncio.gather(*tasks)
    
    # Sort results by index to maintain order
    results.sort(key=lambda x: x[0])
    
    # Save to file
    with open("novel.txt", "w", encoding="utf-8") as f:
        for idx, chapter_text in results:
            if chapter_text:
                chapter_title = chapters[idx][0]
                f.write(f"{chapter_title}\n\n{chapter_text}\n\n")
            else:
                print(f"Chapter {idx} failed to download.")

# Run the script
asyncio.run(main())