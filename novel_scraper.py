import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL of the website (replace with the actual domain)
base_url = "http://23.225.121.240"  # Example from the query

# Fetch HTML content asynchronously
async def fetch_html(session, url):
    for attempt in range(3):  # Retry up to 3 times
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt == 2:
                print(f"Failed to fetch {url} after 3 attempts.")
                return None
            await asyncio.sleep(1)  # Wait before retrying

# Fetch and parse a single page of a chapter
async def fetch_chapter_page(session, url):
    html = await fetch_html(session, url)
    if not html:
        return ""
    soup = BeautifulSoup(html, 'html.parser')
    content_div = soup.find('div', id='content')
    if content_div:
        # Extract text, excluding scripts and unwanted notices
        text = content_div.get_text(separator='\n', strip=True)
        lines = text.split('\n')
        filtered_lines = [line for line in lines if "本章未完，请点击下一页继续阅读" not in line]
        return '\n'.join(filtered_lines)
    return ""

# Fetch all pages of a chapter and combine their content
async def fetch_chapter(session, chapter_url, index):
    try:
        chapter_text = ""
        current_url = chapter_url
        while True:
            page_content = await fetch_chapter_page(session, current_url)
            if not page_content:
                break
            chapter_text += page_content + "\n"
            # Check for next page link
            html = await fetch_html(session, current_url)
            if not html:
                break
            soup = BeautifulSoup(html, 'html.parser')
            next_page_link = soup.find('a', string='下一页')
            if next_page_link and next_page_link['href'] != '#' and '下一章' not in next_page_link.find_parent().text:
                current_url = urljoin(base_url, next_page_link['href'])
            else:
                break
        return index, chapter_text.strip()
    except Exception as e:
        print(f"Error fetching chapter {index}: {e}")
        return index, None

# Wrapper to limit concurrency with a semaphore
async def fetch_chapter_with_semaphore(sem, session, url, index):
    async with sem:
        return await fetch_chapter(session, url, index)

# Extract chapter URLs from a menu page (simplified example)
async def extract_chapter_urls(session, menu_url):
    html = await fetch_html(session, menu_url)
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    # This is a placeholder; adjust based on actual menu page structure
    chapter_links = soup.find_all('a', href=True)  # Simplified for this example
    chapters = []
    for a in chapter_links:
        if '/ldks/95035/' in a['href'] and a.text.strip():
            chapters.append((a.text.strip(), urljoin(base_url, a['href'])))
    return chapters[:5]  # Limit to 5 chapters for demonstration

# Main execution function
async def main():
    menu_url = urljoin(base_url, "/ldks/95035/")  # Chapter list URL
    async with aiohttp.ClientSession() as session:
        # Extract chapter URLs (simplified for this example)
        all_chapters = await extract_chapter_urls(session, menu_url)
        print(f"Found {len(all_chapters)} chapters.")

        # Download chapters in parallel with concurrency limit
        sem = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
        tasks = [fetch_chapter_with_semaphore(sem, session, url, idx) 
                 for idx, (_, url) in enumerate(all_chapters)]
        results = await asyncio.gather(*tasks)
    
    # Sort results by index to ensure correct order
    results.sort(key=lambda x: x[0])

    # Save to file
    output_file = "novel.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, chapter_text in results:
            if chapter_text:
                chapter_title = all_chapters[idx][0]
                f.write(f"{chapter_title}\n\n{chapter_text}\n\n{'='*50}\n\n")
            else:
                print(f"Chapter {idx + 1} failed to download.")
    
    print(f"Novel saved to '{output_file}'.")

# Run the script
if __name__ == "__main__":
    asyncio.run(main())