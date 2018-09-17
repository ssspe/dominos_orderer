import json
import logging

import requests

from decorators import login
from web_driver import wait_for_page_load, scroll_to_element, scroll_to_top, click_button

import Constants as const


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


def customise_pizza(webdriver, pizza_index, pizza, resource_name):
    """
    Makes customisations to the pizza.

    :param webdriver: Selenium webdriver
    :param extra_topping: Toppings that want adding
    :param remove_topping: Toppings that want removing
    """
    pizza['customisation']['extra'] = filter(None, pizza['customisation']['extra'])
    pizza['customisation']['remove'] = filter(None, pizza['customisation']['remove'])

    logging.info(f"Adding pizza {pizza['name']}!")

    webdriver.find_elements_by_xpath(f"//button[@resource-name='{resource_name}']")[
        pizza_index.index(pizza['name'])].click()
    wait_for_page_load(webdriver, "//span[text()='Chicken Breast Strips']")

    if pizza['customisation']['crust'] != "":
        change_crust(webdriver, pizza['customisation']['crust'])

    for topping in pizza['customisation']['extra']:
        element = webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        click_button(element)
        logging.info(f"    + {topping}")

    for topping in pizza['customisation']['remove']:
        element = webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        for clicks in range(2):
            click_button(element)
        logging.info(f"    - {topping}")


def dominos_homepage(webdriver):
    """
    Navigates to the home page of the dominos website

    :param webdriver: The selenium webdriver
    """

    wait_for_page_load(webdriver, "//a[@id='menu-selector']")
    webdriver.find_element_by_xpath("//a[@id='menu-selector']").click()

    wait_for_page_load(webdriver, f"//a[contains(@title,'{const.HALF_AND_HALF}')]")
    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")


def get_json():
    """
    Gets the pizza json, either from the web or from a file

    :return: The pizza json data
    """

    if const.USING_NETWORK_JSON:
        pizza = requests.get(url=const.SERVER_URL)
        data = json.load(pizza)
    else:
        with open("pizza.json", encoding='utf-8') as read_file:
            data = json.load(read_file)

    return data


@login
def process_pizza_json(webdriver):
    """
    Processes the 'pizza' json and order's the pizza

    :param webdriver: Selenium webdriver
    """

    first_half = True
    data = get_json()

    for pizza in data['pizzas']:
        if pizza['type'] == 'full':
            dominos_homepage(webdriver)

            # Getting a list of pizzas on the website menu page
            pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")
            pizza_index = [pizza_text.text for pizza_text in pizzas]

            if pizza['name'] in pizza_index:
                if pizza['customise']:
                    customise_pizza(webdriver, pizza_index, pizza, "Customise")
                    scroll_to_top(webdriver) # Add to order is at the top of the page
                    webdriver.find_element_by_id("add-to-order").click()
                else:
                    # Adding the pizza that is at the index of the pizza name to the basket
                    webdriver.find_elements_by_xpath("//button[@resource-name='AddToBasket']")[
                        pizza_index.index(pizza['name'])].click()
                    logging.info(f"Adding pizza {pizza['name']}!")
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
                click_button(element)
                first_half = not first_half

            wait_for_page_load(webdriver, "//p[text()='Create Your Own']")

            # Have to get list of pizzas again, as create your own is in Half and Half section
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