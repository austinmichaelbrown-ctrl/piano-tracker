import requests
from bs4 import BeautifulSoup
import json
import os
import re

def scrape_listings():
    # Updated URL to the specific search results page provided
    url = "https://www.pianomart.com/buy-a-piano/piano-ads?AdSearchForm%5Bpiano_type_id%5D=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.pianomart.com/"
    }

    try:
        print(f"Attempting to scrape: {url}")
        # Added a timeout to prevent the script from hanging indefinitely
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Server Response: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to retrieve the page. The site might be blocking the request.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # DEBUG: Save what the scraper sees to a file
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        listings = []

        # Based on debug.html, listings are in a specific table structure
        rows = soup.select('table.buy-piano-listing-table tbody tr')
        print(f"Found {len(rows)} potential listing rows. Extracting data...")

        seen_links = set()
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) < 5:
                    continue

                # The image is in the 1st column (index 0)
                img_elem = cols[0].find('img')
                img_url = img_elem['src'] if img_elem else ""

                # The listing link and title are in the 3rd column (index 2)
                link_elem = cols[2].find('a', href=True)
                if not link_elem:
                    continue

                href = link_elem['href']
                full_link = href if href.startswith('http') else "https://www.pianomart.com" + href
                
                if full_link in seen_links:
                    continue

                year = cols[1].get_text(strip=True)
                title = link_elem.get_text(strip=True)
                size_val = cols[3].get_text(strip=True)
                price_text = cols[4].get_text(strip=True)
                state = cols[5].get_text(strip=True)
                city = cols[6].get_text(strip=True)

                # Extract Price
                price_match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', price_text)
                # Defensive check: price_match.group(1) only if match is found
                price_val = 0
                if price_match:
                    try:
                        price_val = int(price_match.group(1).replace(',', ''))
                    except (ValueError, IndexError):
                        price_val = 0
                
                # 5. Determine Brand
                BRANDS = [
                    "Steinway", "Yamaha", "Kawai", "Baldwin", "Mason & Hamlin", "Bechstein", 
                    "Bosendorfer", "Schimmel", "Fazioli", "Knabe", "Petrof", "Young Chang", 
                    "Weber", "Boston", "Essex", "August Förster", "Blüthner", "Grotrian", 
                    "Sauter", "Samick", "Pearl River", "Wurlitzer", "Chickering", "Kimball", 
                    "Korg", "Roland", "Casio", "Suzuki", "Nord", "Dexibell", "Fender Rhodes",
                    "Pleyel", "Gaveau", "Broadwood"
                ]
                
                found_brand = "Other"
                for b in BRANDS:
                    if b.lower() in title.lower():
                        found_brand = b
                        break

                seen_links.add(full_link)
                # Clean up year formatting (handles "1992 - 1993" or "TBA")
                display_year = year.split('-')[0].strip() if '-' in year else year
                
                listings.append({
                    "brand": found_brand,
                    "model": f"{display_year} {title}" if display_year and display_year != "TBA" else title,
                    "image": img_url,
                    "size": size_val, 
                    "price": price_val,
                    "location": f"{city}, {state}" if city and state else state or city or "Unknown",
                    "source": "PianoMart",
                    "link": full_link
                })

            except Exception as row_err:
                print(f"Skipping row due to parsing error: {row_err}")
                continue

        # Fallback/Sample data if scraper finds nothing (to prevent empty UI during testing)
        if not listings:
            print("No listings found, keeping existing data or adding samples.")
            return

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(listings, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully scraped {len(listings)} listings.")

    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    scrape_listings()