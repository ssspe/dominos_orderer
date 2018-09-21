import json
import logging
import os
import sys
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
        logging.warning(f"Cant find Topping {topping}")
        return False

def get_json():
    """
    Process the JSON either from a server or from a file

    :return: Processed pizza json
    """

    if const.USING_NETWORK_JSON:
        pizza = requests.get(url=const.SERVER_URL).json()
        data = pizza['orders']
        pizza = {"pizzas": []}
        for username in data:
            if data[username]["changes"]['base'] != False:
                data[username]["changes"]['toppings']['additions'].append(data[username]["changes"]['base'])

            pizza_info = {'name': data[username]['standard'],
                                  'type': data[username]['size'],
                                  'customise': 1,
                                  'customisation': {
                                      "extra": data[username]["changes"]['toppings']['additions'],
                                      "remove": data[username]["changes"]['toppings']['removals'],
                                      "crust": ""
                          }}

            pizza['pizzas'].append(pizza_info)
        pizza["pizzas"].sort(key=lambda x: x['type']) # Sorting the pizzas into halfs and wholes
        return pizza
    else:
        with open("pizza.json", encoding='utf-8') as read_file:
            data = json.load(read_file)

    return data

def customise_pizza(webdriver, pizza_index, pizza, resource_name):
    """
    Makes customisations to the pizza.

    :param webdriver: Selenium webdriver
    :param extra_topping: Toppings that want adding
    :param remove_topping: Toppings that want removing
    """
    pizza['customisation']['extra'] = filter(None, pizza['customisation']['extra'])
    pizza['customisation']['remove'] = filter(None, pizza['customisation']['remove'])

    logging.info(f"Adding pizza {pizza['name']}! ({pizza['type']})")

    webdriver.find_elements_by_xpath(f"//button[@resource-name='{resource_name}']")[
        pizza_index.index(pizza['name'])].click()
    wait_for_page_load(webdriver, "//span[text()='Chicken Breast Strips']")

    if pizza['customisation']['crust'] != "":
        change_crust(webdriver, pizza['customisation']['crust'])

    for topping in pizza['customisation']['extra']:
        if topping == const.DOMINOS_PIZZA_SAUCE:
            continue
        click_topping(webdriver, topping)
        logging.info(f"    + {topping}")

    for topping in pizza['customisation']['remove']:
        for clicks in range(2):
            click_topping(webdriver, topping)
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


@login
def process_pizza_json(webdriver):
    """
    Processes the 'pizza' json and order's the pizza

    :param webdriver: Selenium webdriver
    """

    first_half = True
    data = get_json()

    for pizza in data['pizzas']:
        if pizza['type'] == 'whole':
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
        elif pizza['type'] == 'half':
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
                #scroll_to_element(webdriver, element)
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
        else:
            logging.warning(f"Unknown pizza: {pizza['name']}")

    logging.info("You're all done here, just pay for your food then you can close the window!")


if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    logging.basicConfig(level=logging.INFO)
    process_pizza_json("")
