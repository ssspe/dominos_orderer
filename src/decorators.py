from web_driver import firefox_web_driver, wait_for_page_load
import Constants as const
from getpass import getpass
def login(func):
    def wrapper(webdriver):
        webdriver = firefox_web_driver(const.DOMINOS_WEBSITE)
        if const.USE_LOGIN:
            webdriver.find_element_by_xpath("//a[text()='Login']").click()
            wait_for_page_load(webdriver, "//label[text()='Email address']")
            webdriver.find_element_by_xpath("//input[@name='email']").send_keys(input("Email: "))
            webdriver.find_element_by_xpath("//input[@name='password']").send_keys(getpass())
            webdriver.find_element_by_xpath("//button[text()='Login']").click()
        else:
            webdriver.find_element_by_xpath("//input[@id='search-input']").send_keys(const.POSTCODE)
            webdriver.find_element_by_xpath("//button[@id='btn-delivery']").click()
            wait_for_page_load(webdriver, "//span[text()='Browse our menu']")
            webdriver.find_element_by_xpath("//span[text()='Browse our menu']").click()
        func(webdriver)
    return wrapper