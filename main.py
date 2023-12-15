import requests
from bs4 import BeautifulSoup
import os
import json
import sys

def get_page_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def extract_links(html, base_url, exclude_list):
    soup = BeautifulSoup(html, 'html.parser')
    links = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href and href.startswith('/') and href not in exclude_list:
            full_url = base_url.rstrip('/') + '/' + href.lstrip('/')
            links[a.text] = full_url
    return links

def extract_details(url):
    page_content = get_page_content(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    h1_tag = soup.find('h1')
    details = {'Title': h1_tag.text.replace('¶', '').strip() if h1_tag else 'Unknown Title'}

    # Extract specific sections and their subsequent <p> contents
    for section in ['Summary', 'Namespace', 'Properties']:
        tag = soup.find(lambda tag: tag.name == 'h2' and section in tag.text)
        if tag:
            content = []
            for sibling in tag.find_next_siblings():
                if sibling.name == 'p':
                    content.append(sibling.text.strip())
                elif sibling.name == 'h2':
                    break
            details[section] = ' '.join(content) if content else 'No content available'

    # Extract Examples
    examples = []
    example_labels = soup.find_all('label', {"for": lambda value: value and value.startswith("__tabbed_")})
    for label in example_labels:
        example_id = label.get('for')
        code_block = soup.find('code', {"tabindex": "0"}, id=example_id)
        if code_block:
            examples.append(code_block.get_text(strip=True))

    details['Examples'] = examples

    return details




def save_to_html_and_json(data, html_path, json_path):
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write('<html><body>')
        for title, details in data.items():
            file.write(f'<h1>{title}</h1>')
            for section in ['Summary', 'Namespace', 'Properties']:
                if section in details:
                    file.write(f'<h2>{section}</h2><p>{details[section]}</p>')
            for example in details.get('Examples', []):
                file.write(f'<h4>Example</h4><pre>{example}</pre>')
        file.write('</body></html>')

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def main():
    base_url = 'https://help.ctrader.com'
    start_url = base_url + '/ctrader-automate/references/'
    exclude_list = ['/ctrader-automate/documentation', '/ctrader-automate/tutorials', 
                    '/ctrader-automate/references', '/ctrader-automate/forum']
    save_path_html = 'cTrader_docu_extracted.html'
    save_path_json = 'cTrader_docu_extracted.json'

    start_page_content = get_page_content(start_url)
    links = extract_links(start_page_content, base_url, exclude_list)
    
    extracted_data = {}
    total_links = len(links)
    for index, (title, url) in enumerate(links.items(), start=1):
        extracted_data[title] = extract_details(url)
        
        # Progress bar
        percentage = (index / total_links) * 100
        sys.stdout.write(f"\rProcessing: {title} ({index}/{total_links}) {percentage:.2f}%")
        sys.stdout.flush()

    save_to_html_and_json(extracted_data, save_path_html, save_path_json)
    print("\nExtraction completed. Data saved in HTML and JSON formats.")

if __name__ == "__main__":
    main()
