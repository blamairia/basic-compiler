import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_phone_models(brand_page_url, base_url):
    phone_models = []
    current_page_url = brand_page_url

    while True:
        response = requests.get(current_page_url)
        if response.status_code != 200:
            print(f"Failed to retrieve {current_page_url}")
            break
        soup = BeautifulSoup(response.text, 'lxml')
        print(f"Scraping phones from {current_page_url}")
        

        # Extract phone models from the current page
        phone_listings = soup.find_all('li')
        for listing in phone_listings:
            phone_name_tag = listing.find('span')
            if phone_name_tag:
                phone_name = phone_name_tag.text.strip()
                print(phone_name)# Extract the phone name
                phone_models.append(phone_name)

        # Check for next page
        next_page_tag = soup.find('a', class_='pages-next')
        if next_page_tag and 'href' in next_page_tag.attrs:
            next_page_url = next_page_tag['href']
            current_page_url = urljoin(base_url, next_page_url)
        else:
            break  # No more pages

    return phone_models

def scrape_phones(main_page_url, base_url):
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.text, 'lxml')

    # Locate the table within the specified div
    main_div = soup.find('div', class_='main main-makers l-box col float-right')
    if not main_div:
        print("Failed to find the main div with brand links")
        return {}

    # Find links to brand pages within the table
    brand_links = main_div.find_all('a', href=True)

    all_phones = {}
    for link in brand_links:
        brand_name = link.text.split('<br>')[0].strip()  # Extract the brand name
        brand_page_partial_url = link['href']
        brand_page_url = urljoin(base_url, brand_page_partial_url)  # Construct the full URL

        all_phones[brand_name] = get_phone_models(brand_page_url, base_url)

    return all_phones


# Usage
base_url = 'https://www.gsmarena.com'  # Replace with the base URL of the website
main_page_url = f'{base_url}/makers.php3'  # Adjust according to the actual URL path
phones_by_brand = scrape_phones(main_page_url, base_url)
print(phones_by_brand)
# Save to CSV
csv_filename = 'phones_by_brand.csv'
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Brand', 'Phone Model'])

    for brand, models in phones_by_brand.items():
        for model in models:
            writer.writerow([brand, model])

print(f"Data saved to {csv_filename}")