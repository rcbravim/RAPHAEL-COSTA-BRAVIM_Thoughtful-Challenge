import logging

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
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
    search_term = get_search_params()

    log.info(f"Opening website {website}")
    open_website(website)

    log.info("Performing search")
    perform_search(search_term)

    log.info('Showing results in console')
    log.info(browser.get_source())


def open_website(url):
    # "https://apnews.com/"
    element_search = '//*[@id="Page-header-trending-zephr"]/div[2]/div[3]/bsp-search-overlay/button'
    
    browser.open_available_browser(url)
    browser.wait_until_element_is_visible(element_search, timeout=10)
    browser.click_element(element_search)
    
def get_search_params():
    workitems.get_input_work_item()
    search_term = workitems.get_work_item_variable("search", "last news")
    return search_term

def perform_search(search_term):
    # "https://apnews.com/"
    search_field = '//*[@id="Page-header-trending-zephr"]/div[2]/div[3]/bsp-search-overlay/div/form/label/input'
    
    browser.input_text(search_field, search_term)
    browser.press_key(search_field, "ENTER")