import requests
from bs4 import BeautifulSoup
import os
import sys

def get_page_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def extract_links(html, base_url, exclude_list):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('/') and href not in exclude_list:
            links.append(base_url + href)
    return links

def save_text_from_links(links, save_path):
    all_text = ""
    total_links = len(links)
    for index, link in enumerate(links, start=1):
        page_content = get_page_content(link)
        soup = BeautifulSoup(page_content, 'html.parser')
        all_text += soup.get_text() + "\n\n"

        # Progress bar
        percentage = (index / total_links) * 100
        sys.stdout.write(f"\rProcessing: {'.' * index} {percentage:.2f}%")
        sys.stdout.flush()
    
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(all_text)
    print(f"\nSaved all extracted text to {save_path}")

def main():
    base_url = 'https://help.ctrader.com'
    start_url = base_url + '/ctrader-automate/references/'
    exclude_list = ['/ctrader-automate/documentation', '/ctrader-automate/tutorials', 
                    '/ctrader-automate/references', '/ctrader-automate/forum']
    save_path = os.path.join(os.path.dirname(__file__), 'cTrader_docu_extracted_from_web.txt')

    start_page_content = get_page_content(start_url)
    links = extract_links(start_page_content, base_url, exclude_list)
    save_text_from_links(links, save_path)

if __name__ == "__main__":
    main()
