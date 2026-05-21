import requests
from bs4 import BeautifulSoup
import json
import os
import time

def scrape_pianomart():
    print("Scraping PianoMart...")
    url = "https://www.pianomart.com/buy-a-piano/view-all-pianos?style=1&finish=1"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
<<<<<<< Updated upstream
        response = requests.get(url, headers=headers)
=======
        print(f"Attempting to scrape: {url}")
        # Added a timeout to prevent the script from hanging indefinitely
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Server Response: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to retrieve the page. The site might be blocking the request.")
            return

>>>>>>> Stashed changes
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        # Updated selector based on common PianoMart listing structure
        items = soup.select('div.card.mb-3') 
        for i, item in enumerate(items):
            try:
                title_element = item.select_one('.card-title')
                price_element = item.select_one('.text-success')
                link_element = item.select_one('a')

                title = title_element.text.strip() if title_element else "Unknown Model"
                price_text = price_element.text.strip() if price_element else "$0"
                price = int(''.join(filter(str.isdigit, price_text))) if price_text else 0
                link = link_element['href'] if link_element else "#"

<<<<<<< Updated upstream
=======
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
                # Ensure we only try to replace/convert if we found a match
                price_val = int(price_match.group(1).replace(',', '')) if (price_match and price_match.group(1)) else 0
                
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
                
>>>>>>> Stashed changes
                listings.append({
                    "id": f"pm-{i}",
                    "brand": title.split(' ')[0],
                    "model": title,
                    "price": price,
                    "size": "Unknown", # PianoMart often requires clicking into detail page for size
                    "source": "PianoMart",
                    "link": "https://www.pianomart.com" + link if not link.startswith('http') else link
                })
            except Exception as item_e:
                print(f"  Error parsing PianoMart item {i}: {item_e}")
                continue
        return listings
    except Exception as e:
        print(f"PianoMart error: {e}")
        return []

def scrape_piano_nation():
    print("Scraping Piano Nation...")
    url = "https://pianonation.com/pianos/pre-owned-pianos/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        # Piano Nation often uses standard WooCommerce structures
        items = soup.select('li.product')
        for i, item in enumerate(items):
            title_element = item.select_one('.woocommerce-loop-product__title')
            price_element = item.select_one('.price')
            link_element = item.select_one('a.woocommerce-LoopProduct-link')

            title = title_element.text.strip() if title_element else "Unknown Model"
            price = int(''.join(filter(str.isdigit, price_element.text))) if price_element else 0
            link = link_element['href'] if link_element else "#"

            # Filter for "grand" pianos, as the page lists all types
            if "grand" in title.lower() and price > 0:
                listings.append({
                    "id": f"pn-{i}",
                    "brand": title.split(' ')[0],
                    "model": title,
                    "price": price,
                    "size": "Baby Grand", # Placeholder, often in description
                    "source": "Piano Nation",
                    "link": link
                })
    except Exception as e:
        print(f"Piano Nation error: {e}")
        return []
    return listings

def scrape_ebay():
    print("Scraping eBay...")
    url = "https://www.ebay.com/sch/i.html?_nkw=black+baby+grand+piano&_sacat=0"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        items = soup.select('.s-item__info')
        for i, item in enumerate(items[1:]): # Skip first item (usually placeholder)
            title_element = item.select_one('.s-item__title')
            price_element = item.select_one('.s-item__price')
            link_element = item.select_one('.s-item__link')

            title = title_element.text.strip() if title_element else "Unknown Model"
            price_text = price_element.text.strip() if price_element else "$0"
            price = int(''.join(filter(str.isdigit, price_text.split('.')[0]))) if price_text else 0
            link = link_element['href'] if link_element else "#"

            listings.append({
                "id": f"eb-{i}",
                "brand": "Other",
                "model": title,
                "price": price,
                "size": "Baby Grand", # Placeholder, often in description
                "source": "eBay",
                "link": link
            })
        return listings
    except Exception as e:
        print(f"eBay error: {e}")
        return []

def main():
    print("Starting piano price crawl...")
    all_results = []
    all_results.extend(scrape_pianomart())
    time.sleep(2) # Be polite, wait a bit before next request
    all_results.extend(scrape_piano_nation())
    time.sleep(2) # Be polite, wait a bit before next request
    all_results.extend(scrape_ebay())

    file_path = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(file_path, 'w') as f:
        json.dump(all_results, f, indent=4)
    print(f"Success! {len(all_results)} listings saved to data.json")

if __name__ == "__main__":
    # You will need to install dependencies: pip install requests beautifulsoup4
    main()