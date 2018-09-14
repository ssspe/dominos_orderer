import json
import time
import logging
from web_driver import firefox_web_driver, wait_for_page_load, scroll_to_element

POSTCODE = "BA147FP"
DOMINOS_WEBSITE = "https://www.dominos.co.uk/menu"
HALF_AND_HALF = "Torn between two pizzas"


def click_topping(webdriver, topping):
    """
    Clicks a topping on the customisation page

    :input webdriver: The selenium webdriver
    :input topping: The topping to click
    :return: Boolean if the click was successful
    """

    try:
        if topping != "":
            webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        return True
    except:
        logging.warning("Cant find Topping")
        return False


def customise_pizza(webdriver, pizza_index, pizza, resource_name):
    """
    Makes customisations to the pizza.

    :param webdriver: The selenium webdriver
    :param extra_topping: Toppings that want adding
    :param remove_topping: Toppings that want removing
    """

    is_customised = True

    webdriver.find_elements_by_xpath(f"//button[@resource-name='{resource_name}']")[
        pizza_index.index(pizza['name'])].click()
    wait_for_page_load(webdriver, "//span[text()='Chicken Breast Strips']")

    for topping in pizza['customisation']['extra']:
        if not click_topping(webdriver, topping):
            is_customised = False
        logging.info(f"Added {topping} to the pizza.")

    for topping in pizza['customisation']['remove']:
        for clicks in range(2):
            if not click_topping(webdriver, topping):
                is_customised = False
        logging.info(f"Removed {topping} from the pizza.")

    if not is_customised:
        # For some reason dominos has an overlay that stops selenium from working 50% of the time
        logging.warning("Error with dominos, trying again.")
        webdriver.close()
        process_pizza_json()


def dominos_homepage(webdriver):
    """
    Navigates to the home page of the dominos website using the global POSTCODE

    :param webdriver: The selenium webdriver
    """

    webdriver.find_element_by_id("search-input").send_keys(POSTCODE)
    webdriver.find_element_by_id("btn-delivery").click()

    wait_for_page_load(webdriver, "//span[text()='Browse our menu']")
    webdriver.find_element_by_xpath("//span[text()='Browse our menu']").click()

    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")


def process_pizza_json():
    """
    Processes the 'pizza' json and order's the pizza
    """

    first_half = True
    with open("pizza.json", "r") as read_file:
        data = json.load(read_file)

    webdriver = firefox_web_driver(DOMINOS_WEBSITE)
    dominos_homepage(webdriver)

    for pizza in data['pizzas']:
        if pizza['type'] == 'full':
            wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")
            pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")
            pizza_index = [pizza.text for pizza in pizzas]

            if pizza['customise']:
                logging.info(f"Customizing pizza {pizza['name']}!")

                if pizza['name'] in pizza_index:
                    customise_pizza(webdriver, pizza_index, pizza, "Customise")
                    webdriver.find_element_by_xpath("//button[text()='Add To Order']").click()
                    
            else:
                if pizza['name'] in pizza_index:
                    webdriver.find_elements_by_xpath("//button[@resource-name='AddToBasket']")[
                        pizza_index.index(pizza['name'])].click()
        else:
            if first_half:
                webdriver.find_element_by_xpath(f"//a[contains(@title,'{HALF_AND_HALF}')]").click()
                wait_for_page_load(webdriver, "//h2[text()='Create Left Half']")
                webdriver.find_element_by_xpath("//h2[text()='Create Left Half']").click()
                first_half = not first_half
            else:
                wait_for_page_load(webdriver, "//h2[text()='Create Right Half']")
                element = webdriver.find_element_by_xpath("//h2[text()='Create Right Half']")
                scroll_to_element(webdriver, element)
                element.click()
                first_half = not first_half

            if pizza['customise']:
                logging.info(f"Customizing pizza {pizza['name']}!")
                wait_for_page_load(webdriver, "//p[text()='Create Your Own']")
                pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")
                pizza_index = [pizza.text for pizza in pizzas]

                if pizza['name'] in pizza_index:
                    customise_pizza(webdriver, pizza_index, pizza, "Choose")

            if first_half:
                wait_for_page_load(webdriver, "//button[text()='Add To Order']")
                time.sleep(1)
                webdriver.find_element_by_xpath("//button[text()='Add To Order']").click()

    time.sleep(100)


if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    process_pizza_json()