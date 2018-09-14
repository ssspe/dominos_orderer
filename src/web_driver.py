from selenium import webdriver
import time

def firefox_web_driver(url_number):
    driver = webdriver.Firefox()
    web = driver
    web.get(url_number)
    return web

# noinspection PyBroadException
def wait_for_page_load(webdriver, finder, set_timeout=60):
    """
    Waits till a specific element is displayed before returning from an infinite loop.

    Note: There is a timeout of 60 seconds on any element
    :param webdriver: The Selenium webdriver used to connect to the Pakscan
    :param finder: The element used by the webdriver to find
    :param set_timeout: A set timeout if 60 seconds is not long enough
    :return: Returns True if the element is found
    """

    timeout = time.time() + set_timeout
    print(f"waiting on {finder}")
    while True:
        try:
            if webdriver.find_element_by_xpath(finder).is_displayed():
                return
        except:
            if time.time() > timeout:
                assert False, f"Timed out waiting for element: {finder}"
            continue