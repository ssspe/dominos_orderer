import logging
import time

from selenium import webdriver

def custom_web_driver(url_number, download_path=""):
    """
    Sets up a Chromium web driver to connect to a custom url

    :param url_number: The url to connect to
    :param download_path: The download path of the chrome web driver
    :return: Returns the web driver instance
    """

    # Setting the preferences of the chrome driver
    logging.info(f"Connecting to {url_number} using the Chrome Selenium webdriver.")
    prefs = {'download.default_directory': download_path}
    moreprefs = {'safebrowsing.enabled': True}
    prefs.update(moreprefs)

    # Setting the options of the chrome browser
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option('prefs', prefs)
    opts.add_argument('--safebrowsing-disable-download-protection')
    opts.add_argument("start-maximized")

    driver = webdriver.Chrome(options=opts)

    web = driver
    web.get(url_number)
    logging.info(f"Connected to {url_number}.")

    return web

def click_topping(webdriver, topping):
    try:
        webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
    except:
        print("Cant find Topping")

def customise_pizza(webdriver, extra_topping, remove_topping):
    for topping in extra_topping:
        try:
            webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        except:
            return False
        print(f"Added {topping} to the pizza.")

    for topping in remove_topping:
        try:
            webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        except:
            return False
        try:
            webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        except:
            return False
        print(f"Removed {topping} from the pizza.")

    # Sometimes an overlay can block the button so try it twice
    for attempts in range(2):
        try:
            webdriver.execute_script("document.querySelector('#add-to-order').click();")
            time.sleep(1)
        except:
            continue

    return True

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

if __name__ == "__main__":
    my_pizza = "Ham & Pineapple"
    customise = True

    webdriver = custom_web_driver("https://www.dominos.co.uk/menu")
    webdriver.find_element_by_id("search-input").send_keys("BA147FP")
    webdriver.find_element_by_id("btn-delivery").click()

    wait_for_page_load(webdriver, "//span[text()='Browse our menu']")
    webdriver.find_element_by_xpath("//span[text()='Browse our menu']").click()

    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")
    pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")

    pizza_index = {}
    for index, pizza in enumerate(pizzas):
        pizza_index[pizza.text] = index

    if customise:
        print("Customizing pizza!")

        if my_pizza in pizza_index.keys():
            webdriver.find_elements_by_xpath("//button[@resource-name='Customise']")[pizza_index[my_pizza]].click()

        time.sleep(5)
        did_customise = customise_pizza(webdriver, ["Mushrooms", "Sweetcorn"], ["Pineapple"])
        if not did_customise:
            customise_pizza(webdriver, ["Mushrooms", "Sweetcorn"], ["Pineapple"])
    else:
        if my_pizza in pizza_index.keys():
            webdriver.find_elements_by_xpath("//button[@resource-name='AddToBasket']")[pizza_index[my_pizza]].click()
    time.sleep(100)

