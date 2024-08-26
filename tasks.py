import logging
from datetime import datetime, timedelta

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
import requests
from robocorp.tasks import task
import os
import re

logging.basicConfig(level=os.getenv("LOGGER_LEVEL", "INFO"), format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger()

browser = Selenium()
excel = Files()
workitems = WorkItems()
website = "https://apnews.com/"  # category not applicable
timeout = 10


@task
def main():
    log.info("Getting input parameters")
    search_term, category, months = get_search_params()

    log.info(f"Opening website {website}")
    open_website(website)

    log.info("Performing search")
    perform_search(search_term)

    log.info("Extracting data")
    news_data = extract_data(months)

    log.info('Saving data to Excel')
    save_to_excel(news_data)


def open_website(url):
    element_search_button = 'css:.SearchOverlay-search-button'
    browser.open_available_browser(url)
    browser.wait_until_element_is_visible(element_search_button, timeout=timeout)


def get_search_params():
    workitems.get_input_work_item()
    search_term = workitems.get_work_item_variable("search", "last news")
    category = workitems.get_work_item_variable("category", None)
    months = workitems.get_work_item_variable("months", 1)
    return search_term, category, months


def perform_search(search_term):
    element_search_button = 'css:.SearchOverlay-search-button'
    browser.wait_until_element_is_visible(element_search_button, timeout=timeout)
    browser.click_element(element_search_button)

    element_search_input = 'css:.SearchOverlay-search-input'
    browser.input_text(element_search_input, search_term)
    browser.press_keys(element_search_input, "ENTER")

    element_sort_filter = 'css:.SearchResultsModule-sorts'
    browser.wait_until_element_is_visible(element_sort_filter, timeout=timeout)
    browser.press_keys(element_sort_filter, "N", 'ENTER')


def extract_data(months):
    search_results = 'css:.SearchResultsModule-results'
    browser.wait_until_element_is_visible(search_results)
    search_results_element = browser.find_element(search_results)
    page_list_element = 'css:.PageList-items-item'
    title_element = 'css:.PagePromo-title'
    description_element = 'css:.PagePromo-description'
    picture_element = 'css:.PagePromo-media img'

    extracted_data = []
    news_items = browser.find_elements(page_list_element, parent=search_results_element)
    for count, item in enumerate(news_items, start=1):
        log.info(f"Processing News: [{count}/{len(news_items)}]")

        # date related
        date = check_date_apnews(item, months)
        if not date:
            continue

        # title and description related
        title = browser.find_element(title_element, parent=item).text
        description = browser.find_element(description_element, parent=item).text

        # image related
        image_element = browser.find_elements(picture_element, parent=item)
        picture_filename = 'N/A'
        if image_element:
            image_url = image_element[0].get_attribute("src")
            picture_filename = '-'.join(title.split(' ')[:10]) + '.jpg'
            download_image(image_url, picture_filename)

        extracted_data.append({
            "title": title,
            "description": description,
            "date": date,
            "picture filename": picture_filename,
            "count phrases title": len(title.split(' ')),
            "count phrases description": len(description.split(' ')),
            "contains money": bool(re.search(r'\$\d+|\d+\s+(dollars|USD)', description)),
        })

    return extracted_data


def download_image(url, filename):
    response = requests.get(url)
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def check_date_apnews(item, months):
    date = None
    date_elements = ['css:.Timestamp-template', 'css:.Timestamp-template-now']
    for date_element in date_elements:
        date_element = browser.find_elements(date_element, parent=item)
        if date_element:
            date = date_element[0].text
            break

    period = datetime.now() - timedelta(days=months * 30)
    if date:
        date = date[0].text

        if ',' in date:
            if len(date.split(' ')) > 1:
                date = datetime.strptime(date, "%B %d, %Y")
            else:
                date = datetime.strptime(date, f"%B %d, {datetime.now().year}")
        elif date == 'Yesterday':
            date = datetime.now() - timedelta(days=1)
        elif date == 'Today' or 'ago' in date:
            date = datetime.now()

        if isinstance(datetime, date):
            if date < period:
                return False
            return date.date()

    return 'Unknown date'


def save_to_excel(news_items):
    output_file = os.path.join("output", "news_data.xlsx")
    excel.create_workbook(output_file)
    headers = [
        "Title", "Description", "Date", "Picture Filename",
        "Count Phrases Title", "Count Phrases Description", "Contains Money"
    ]
    excel.append_rows_to_worksheet([headers])
    excel.append_rows_to_worksheet(news_items)
    excel.save_workbook()
