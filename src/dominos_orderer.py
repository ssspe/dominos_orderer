import json
import time
import logging

from web_driver import firefox_web_driver, wait_for_page_load

POSTCODE = "BA147FP"

def click_topping(webdriver, topping):
    try:
        webdriver.find_element_by_xpath(f"//span[text()='{topping}']").click()
        return True
    except:
        logging.warning("Cant find Topping")
        return False

def customise_pizza(webdriver, extra_topping, remove_topping):
    for topping in extra_topping:
        if not click_topping(webdriver, topping):
            return False
        logging.info(f"Added {topping} to the pizza.")

    for topping in remove_topping:
        for clicks in range(2):
            if not click_topping(webdriver, topping):
                return False
        logging.info(f"Removed {topping} from the pizza.")

    # Sometimes an overlay can block the button so try it twice
    for attempts in range(2):
        try:
            webdriver.execute_script("document.querySelector('#add-to-order').click();")
        except:
            continue

    return True

def dominos_homepage(webdriver):
    webdriver.find_element_by_id("search-input").send_keys(POSTCODE)
    webdriver.find_element_by_id("btn-delivery").click()

    wait_for_page_load(webdriver, "//span[text()='Browse our menu']")
    webdriver.find_element_by_xpath("//span[text()='Browse our menu']").click()

    wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")

def start():
    with open("pizza.json", "r") as read_file:
        data = json.load(read_file)

    webdriver = firefox_web_driver("https://www.dominos.co.uk/menu")
    dominos_homepage(webdriver)

    pizzas = webdriver.find_elements_by_xpath("//div[@class='product-variant-name-simple']")

    pizza_index = {}
    for index, pizza in enumerate(pizzas):
        pizza_index[pizza.text] = index
    pizza_index = [pizza.text for pizza in pizzas]

    for pizza in data['pizzas']:
        wait_for_page_load(webdriver, "//span[text()='Speciality Pizzas']")
        if pizza['customise']:
            logging.info(f"Customizing pizza {pizza['name']}!")

            if pizza['name'] in pizza_index:
                webdriver.find_elements_by_xpath("//button[@resource-name='Customise']")[pizza_index.index(pizza['name'])].click()

                wait_for_page_load(webdriver, "//span[text()='Chicken Breast Strips']")
                is_customised = customise_pizza(webdriver, pizza['customisation']['extra'], pizza['customisation']['remove'])
                if not is_customised:
                    # For some reason dominos has an overlay that stops selenium
                    # from working 50% of the time
                    logging.warning("Error with dominos, trying again.")
                    webdriver.close()
                    start()
        else:
            if data['name'] in pizza_index:
                webdriver.find_elements_by_xpath("//button[@resource-name='AddToBasket']")[pizza_index.index(pizza['name'])].click()

    time.sleep(100)


if __name__ == "__main__":
    logging.basicConfig(filename='example.log')
    start()