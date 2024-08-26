import logging

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
import requests
from robocorp.tasks import task
import os

logging.basicConfig(level=os.getenv("LOGGER_LEVEL", "INFO"), format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger()

browser = Selenium()
excel = Files()
workitems = WorkItems()
website = "https://apnews.com/"


@task
def main():
    log.info("Getting input parameters")
    search_term, category, months = get_search_params()

    log.info(f"Opening website {website}")
    open_website(website)

    log.info("Performing search")
    perform_search(search_term)

    log.info("Extracting data")
    news_data = extract_data()

    log.info('Showing results in console')
    log.info(news_data)

def open_website(url):
    # "https://apnews.com/"
    element_search = '//*[@id="Page-header-trending-zephr"]/div[2]/div[3]/bsp-search-overlay/button'
    
    browser.open_available_browser('about:blank')
    browser.go_to(url)
    browser.wait_until_element_is_visible(element_search, timeout=10)
    browser.click_element(element_search)
    
def get_search_params():
    workitems.get_input_work_item()
    search_term = workitems.get_work_item_variable("search", "last news")
    category = workitems.get_work_item_variable("category", None)
    months = workitems.get_work_item_variable("months", 1)
    return search_term, category, months

def perform_search(search_term):
    # "https://apnews.com/"
    search_element = '//*[@id="Page-header-trending-zephr"]/div[2]/div[3]/bsp-search-overlay/div/form/label/input'
    
    browser.input_text(search_element, search_term)
    browser.press_keys(search_element, "ENTER")

def extract_data():
    # "https://apnews.com/"
    search_results = 'css:.SearchResultsModule-results'
    search_results_element = browser.find_element(search_results)
    page_list_element = 'css:.PageList-items-item'
    title_element = 'css:.PagePromo-title'
    description_element = 'css:.PagePromo-description'
    date_elements = ['css:.Timestamp-template', 'css:.Timestamp-template-now']
    picture_element = 'css:.PagePromo-media img'
    
    extrated_data = []
    news_items = browser.find_elements(page_list_element, parent=search_results_element)
    for count, item in enumerate(news_items, start=1):
        log.info(f"Processing news: [{count}/{len(news_items)}]")

        # title and description
        title = browser.find_element(title_element, parent=item).text
        description = browser.find_element(description_element, parent=item).text

        # image
        image_element = browser.find_elements(picture_element, parent=item)
        picture_filename = 'N/A'
        if image_element:
            image_url = image_element[0].get_attribute("src")
            picture_filename = '-'.join(title.split(' ')[:10]) + '.jpg'
            download_image(image_url, picture_filename)

        # date
        date = 'N/A'
        for date_element in date_elements:
            date_element = browser.find_elements(date_element, parent=item)
            if date_element:
                date = date_element[0].text
                break
            
        extrated_data.append({
            "title": title,
            "description": description,
            "date": date,
            "picture filename": picture_filename,
            "count phrases title": len(title.split(' ')),
            "count phrases description": len(description.split(' ')),
        })

    return extract_data

def download_image(url, filename):
    response = requests.get(url)
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
