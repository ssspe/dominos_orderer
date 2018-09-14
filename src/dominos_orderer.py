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
        error_restart(webdriver)

def error_restart(webdriver):
    """
    Restarts the program after an error, not the cleanest solution but it works
    """

    # For some reason dominos has an overlay that stops selenium from working 20% of the time
    logging.warning("Error with dominos, trying again.")
    webdriver.close()
    process_pizza_json(webdriver)


def dominos_homepage(webdriver):
    """
    Navigates to the home page of the dominos website using the global POSTCODE

    :param webdriver: The selenium webdriver
    """

    wait_for_page_load(webdriver, "//a[@id='menu-selector']")
    webdriver.find_element_by_xpath("//a[@id='menu-selector']").click()

    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")


def login(func):
    def wrapper(webdriver):
        webdriver = firefox_web_driver(DOMINOS_WEBSITE)
        webdriver.find_element_by_xpath("//a[text()='Login']").click()
        wait_for_page_load(webdriver, "//label[text()='Email address']")
        webdriver.find_element_by_xpath("//input[@name='email']").send_keys(input("Email: "))
        webdriver.find_element_by_xpath("//input[@name='password']").send_keys(input("Password: "))
        webdriver.find_element_by_xpath("//button[text()='Login']").click()
        func(webdriver)
    return wrapper

@login
def process_pizza_json(webdriver):
    """
    Processes the 'pizza' json and order's the pizza
    """

    first_half = True
    dominos_homepage(webdriver)

    with open("pizza.json", "r") as read_file:
        data = json.load(read_file)

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
                try:
                    time.sleep(1)
                    webdriver.find_element_by_xpath("//button[text()='Add To Order']").click()
                except:
                    error_restart(webdriver)

    input("You're all done here, just pay for your food then you can close the window!")


if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    process_pizza_json("")