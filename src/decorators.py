from web_driver import firefox_web_driver, wait_for_page_load
import Constants as const
def login(func):
    def wrapper(webdriver):
        webdriver = firefox_web_driver(const.DOMINOS_WEBSITE)
        webdriver.find_element_by_xpath("//a[text()='Login']").click()
        wait_for_page_load(webdriver, "//label[text()='Email address']")
        webdriver.find_element_by_xpath("//input[@name='email']").send_keys(input("Email: "))
        webdriver.find_element_by_xpath("//input[@name='password']").send_keys(input("Password: "))
        webdriver.find_element_by_xpath("//button[text()='Login']").click()
        func(webdriver)
    return wrapper