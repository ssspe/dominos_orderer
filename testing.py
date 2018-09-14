import json
import time

from selenium import webdriver

def firefox_web_driver(url_number):
    driver = webdriver.Firefox()
    web = driver
    web.get(url_number)
    return web

def click_topping(webdriver, topping):
    try:
        webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        return True
    except:
        print("Cant find Topping")
        return False

def customise_pizza(webdriver, extra_topping, remove_topping):
    for topping in extra_topping:
        print(topping)
        if not click_topping(webdriver, topping):
            return False
        print(f"Added {topping} to the pizza.")

    for topping in remove_topping:
        print(topping)
        for clicks in range(2):
            if not click_topping(webdriver, topping):
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

def start():
    with open("pizza.json", "r") as read_file:
        data = json.load(read_file)

    webdriver = firefox_web_driver("https://www.dominos.co.uk/menu")
    webdriver.find_element_by_id("search-input").send_keys("BA147FP")
    webdriver.find_element_by_id("btn-delivery").click()

    wait_for_page_load(webdriver, "//span[text()='Browse our menu']")
    webdriver.find_element_by_xpath("//span[text()='Browse our menu']").click()

    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")
    pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")

    pizza_index = {}
    for index, pizza in enumerate(pizzas):
        pizza_index[pizza.text] = index

    if data['customise']:
        print(f"Customizing pizza {data['name']}!")

        if data['name'] in pizza_index.keys():
            webdriver.find_elements_by_xpath("//button[@resource-name='Customise']")[pizza_index[data['name']]].click()

            wait_for_page_load(webdriver, "//span[text()='Chicken Breast Strips']")
            is_customised = customise_pizza(webdriver, data['customisation']['extra'], data['customisation']['remove'])
            if not is_customised:
                webdriver.close()
                start()
    else:
        if data['name'] in pizza_index.keys():
            webdriver.find_elements_by_xpath("//button[@resource-name='AddToBasket']")[pizza_index[data['name']]].click()

    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")
    time.sleep(100)


if __name__ == "__main__":
    start()