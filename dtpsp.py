import configparser
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Config logger
logging.basicConfig(level=logging.INFO)

# Read the configuration
config = configparser.ConfigParser()
config.read('settings.ini')
logging.debug("Read the configuration. Base URL is [%s]", config['system']['base_url'])

petition_url = config['system']['base_url']
gecko_driver_binary_path = config['system']['firefox_gecko_path']

# Config and start selenium driver
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, executable_path=gecko_driver_binary_path)
driver.implicitly_wait(1)
driver.get(petition_url)


def read_signers_from_page(driver):
    signed_records = []
    table_elements = driver.find_elements(by=By.XPATH,
                                          value="//div[@class='table_row']")
    logging.info("Found %s records on page", len(table_elements))
    for element in table_elements:
        signed_records.append(element.text)

    return signed_records


signers_button = driver.find_element(by=By.XPATH, value="//a[@data-id='pet-tab-3']")
signers_button.click()
number_of_pages = driver.find_element(by=By.XPATH, value="//ul[@class='pag_list']/li[@class='pag_child'][last()-1]").text
logging.info("Found %s pages of signers", number_of_pages)

all_signers = []
for page in range(1, int(number_of_pages) + 1):
    logging.info("Processing page %s", page)
    page_btn = driver.find_element(by=By.XPATH, value="//ul[@class='pag_list']/li[@class='pag_child']/a[text()='{}']".format(page))
    page_btn.click()
    # Wait for the button to become active. This meand that the part of the DOM with signers is updated.
    # Prevents StaleElementReferenceException.
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//ul[@class='pag_list']/li[@class='pag_child']/a[@class='pag_link active' and text()='{}']".format(page)))
    )
    signers_from_page = read_signers_from_page(driver)
    all_signers.extend(signers_from_page)

print(*all_signers, sep="\n")




