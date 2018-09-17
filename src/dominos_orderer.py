import json
import time
import logging

from decorators import login
from web_driver import wait_for_page_load, scroll_to_element, scroll_to_top, click_button
from selenium.webdriver.common.action_chains import ActionChains

import Constants as const


def error_restart(webdriver):
    """
    Restarts the program after an error, not the cleanest solution but it works

    :param webdriver: Selenium webdriver
    """

    # For some reason dominos has an overlay that stops selenium from working 20% of the time
    logging.warning("Error with dominos, trying again.")
    webdriver.close()
    process_pizza_json(webdriver)


def change_crust(webdriver, crust):
    """
    Change the crust of the pizza

    :param webdriver: Selenium webdriver
    :param crust: What crust to change to
    """

    if crust in const.CRUSTS.keys():
        if const.CRUSTS[crust]:
            webdriver.find_element_by_xpath("//i[@class#'icon-chevron-right carousel-control-icon is-clickable']")
        webdriver.find_element_by_xpath(f"//p[contains(text(), '{crust}')]").click()
        logging.info(f"    {crust}")


def click_topping(webdriver, topping):
    """
    Clicks a topping on the customisation page

    :param webdriver: Selenium webdriver
    :param topping: The topping to click
    :return: Boolean if the click was successful
    """

    try:
        webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        return True
    except:
        logging.warning("Cant find Topping")
        return False


def customise_pizza(webdriver, pizza_index, pizza, resource_name):
    """
    Makes customisations to the pizza.

    :param webdriver: Selenium webdriver
    :param extra_topping: Toppings that want adding
    :param remove_topping: Toppings that want removing
    """

    is_customised = True
    logging.info(f"Adding pizza {pizza['name']}!")

    webdriver.find_elements_by_xpath(f"//button[@resource-name='{resource_name}']")[
        pizza_index.index(pizza['name'])].click()
    wait_for_page_load(webdriver, "//span[text()='Chicken Breast Strips']")

    if pizza['customisation']['crust'] != "":
        change_crust(webdriver, pizza['customisation']['crust'])

    for topping in pizza['customisation']['extra']:
        if topping != "":
            if not click_topping(webdriver, topping):
                is_customised = False
            logging.info(f"    + {topping}")

    for topping in pizza['customisation']['remove']:
        if topping != "":
            for clicks in range(2):
                if not click_topping(webdriver, topping):
                    is_customised = False
            logging.info(f"    - {topping}")

    if not is_customised:
        error_restart(webdriver)


def dominos_homepage(webdriver):
    """
    Navigates to the home page of the dominos website

    :param webdriver: The selenium webdriver
    """

    wait_for_page_load(webdriver, "//a[@id='menu-selector']")
    webdriver.find_element_by_xpath("//a[@id='menu-selector']").click()

    wait_for_page_load(webdriver, f"//a[contains(@title,'{const.HALF_AND_HALF}')]")
    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")


@login
def process_pizza_json(webdriver):
    """
    Processes the 'pizza' json and order's the pizza

    :param webdriver: Selenium webdriver
    """

    first_half = True

    with open("pizza.json", encoding='utf-8') as read_file:
        data = json.load(read_file)

    for pizza in data['pizzas']:
        if pizza['type'] == 'full':
            dominos_homepage(webdriver)
            # Getting a list of pizzas on the website menu page
            pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")
            pizza_index = [pizza_text.text for pizza_text in pizzas]

            if pizza['customise']:
                if pizza['name'] in pizza_index:
                    customise_pizza(webdriver, pizza_index, pizza, "Customise")
                    scroll_to_top(webdriver) # Add to order is at the top of the page
                    webdriver.find_element_by_id("add-to-order").click()
                    
            else:
                if pizza['name'] in pizza_index:
                    logging.info(f"Adding pizza {pizza['name']}!")
                    # Adding the pizza that is at the index of the pizza name to the basket
                    webdriver.find_elements_by_xpath("//button[@resource-name='AddToBasket']")[
                        pizza_index.index(pizza['name'])].click()
        else:
            if first_half:
                dominos_homepage(webdriver)
                element = webdriver.find_element_by_xpath(f"//a[contains(@title,'{const.HALF_AND_HALF}')]")

                click_button(element)

                wait_for_page_load(webdriver, "//h2[text()='Create Left Half']")
                webdriver.find_element_by_xpath("//h2[text()='Create Left Half']").click()
                first_half = not first_half
            else:
                wait_for_page_load(webdriver, "//h2[text()='Create Right Half']")
                element = webdriver.find_element_by_xpath("//h2[text()='Create Right Half']")
                scroll_to_element(webdriver, element)
                element.click()
                first_half = not first_half

            wait_for_page_load(webdriver, "//p[text()='Create Your Own']")
            pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")
            pizza_index = [pizza.text for pizza in pizzas]

            if pizza['name'] in pizza_index:
                customise_pizza(webdriver, pizza_index, pizza, "Choose")

            if first_half:
                scroll_to_top(webdriver)
                webdriver.find_element_by_id("add-to-order").click()

    input("You're all done here, just pay for your food then you can close the window!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_pizza_json("")