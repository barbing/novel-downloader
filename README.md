# Novel Downloader (Async Python Scraper)

A small async Python toolkit to download online novels chapter-by-chapter and save them into a local `.txt` file.

This repo currently includes **three scripts**:
- `extract_panda_seq.py`: downloads chapters sequentially and saves to `novel.txt`. :contentReference[oaicite:0]{index=0}  
- `extract_panda_para.py`: downloads chapters concurrently (parallel) and saves to `<BookTitle>.txt`. :contentReference[oaicite:1]{index=1}  
- `novel_scraper.py`: a more generic scraper with retries + “next page” handling for multi-page chapters. :contentReference[oaicite:2]{index=2}  

---

## Features

- **Async fetching** via `aiohttp` + `asyncio` for fast downloads (parallel version included). 
- **HTML parsing** using `BeautifulSoup4` to extract chapter links and text. 
- **Ordered output**: chapters are saved in the correct sequence even when downloaded concurrently. 
- Optional: **multi-page chapter** support (clicking “下一页”) and **retry logic** in `novel_scraper.py`. :contentReference[oaicite:6]{index=6}

---

## Requirements

- Python 3.9+ recommended
- Dependencies:
  - `aiohttp`
  - `beautifulsoup4`

Install:

```bash
pip install aiohttp beautifulsoup4
