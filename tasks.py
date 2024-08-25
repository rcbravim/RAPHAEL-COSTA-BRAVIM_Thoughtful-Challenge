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


@task
def main():
    website = "https://apnews.com/"
    log.info(f"Opening website {website}")
    open_website(website)


def open_website(url):
    # "https://apnews.com/"
    element_search = '//*[@id="Page-header-trending-zephr"]/div[2]/div[3]/bsp-search-overlay/button'
    
    browser.open_available_browser(url)
    browser.wait_until_element_is_visible(element_search, timeout=10)
    browser.click_element(element_search)
