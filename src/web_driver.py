from selenium import webdriver
import time
import logging

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def firefox_web_driver(url_number):
    """
    The web driver selenium controls, using firefox as chrome had issues with dominos

    :param url_number: The URL like to dominos
    :return: The driver object
    """
    driver = webdriver.Firefox()
    web = driver
    web.get(url_number)
    return web

# noinspection PyBroadException
def wait_for_page_load(webdriver, finder, set_timeout=40):
    """
    Waits till a specific element is displayed before returning from an infinite loop.

    Note: There is a timeout of 60 seconds on any element
    :param webdriver: The Selenium webdriver
    :param finder: The xpath element to find
    :param set_timeout: A set timeout if 20 seconds is not long enough
    :return: Returns True if the element is found
    """

    timeout = time.time() + set_timeout
    logging.debug(f"waiting on {finder}")
    while True:
        try:
            if webdriver.find_element_by_xpath(finder).is_displayed():
                return
        except:
            if time.time() > timeout:
                assert False, f"Timed out waiting for element: {finder}"
            continue

def scroll_to_element(webdriver, element, scroll=-150):
    """
    Brings the specified element into view

    :input webdriver: The Selenium webdriver
    :input element: The element to scroll to
    """

    try:
        actions = ActionChains(webdriver)
        actions.move_to_element(element).perform()
        webdriver.execute_script(f"window.scrollBy(0, {scroll});")
        time.sleep(1)
    except:
        logging.warning(f"Could not scroll to element: {element}")

def scroll_to_top(webdriver):
    """
    Scrolls to the top of the window. Useful when elements are hidden

    :param webdriver: The Selenium webdriver
    """
    webdriver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(10) # Have to sleep to allow dominos server to catch up


def click_button(element):
    # This seems to be the only way to make this work reliably, if theres a better way
    # change it
    count = 0

    while count < 5:
        try:
            element.click()
            return
        except:
            time.sleep(1)
            count += 1
            continue