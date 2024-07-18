from selenium import webdriver
from selenium.webdriver.common.by import By
import time


card_to_file = []
def run_driver(browser):
    global driver
    if browser == 'chrom':
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
    elif browser == 'edge':
        driver = webdriver.Edge()
        driver.maximize_window()
    elif browser == 'firefox':
        driver = webdriver.Firefox()
        driver.maximize_window()
    driver.get('https://www.olx.ua/uk/')
    driver.implicitly_wait(20)

    return driver


def choice_things(thing, region, location):
    thing_to_search = driver.find_element(By.ID, "search")
    thing_to_search.send_keys(f"{thing}")
    time.sleep(3)
    driver.find_element(By.ID, "location-input").click()
    time.sleep(3)
    reg1 = driver.find_element(By.XPATH, f"//span[text()='{region} область']/parent::div/parent::li")
    driver.execute_script("arguments[0].scrollIntoView({behavior:\"auto\", block:\"center\", inline:\"center\"});", reg1)
    time.sleep(5)
    reg1.click()
    if location == 'область':
        print(22, location, region)
        reg2 = driver.find_element(By.CSS_SELECTOR, "div[data-cy= 'all-cities']")
        driver.execute_script("arguments[0].scrollIntoView({behavior:\"auto\", block:\"center\", inline:\"center\"});", reg2)
        time.sleep(5)
        reg2.click()
    else:
        reg2 = driver.find_element(By.XPATH, f"//li[text()='{location}']")
        driver.execute_script("arguments[0].scrollIntoView({behavior:\"auto\", block:\"center\", inline:\"center\"});", reg2)
        time.sleep(5)
        reg2.click()
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, '[name="searchBtn"]').click()
    time.sleep(4)
    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-cy= 'l-card']")
    return cards


def get_things(id2, max_price, card):
    time.sleep(4)
    # id = card.get_attribute('id')
    image_link = card.find_element(By.TAG_NAME, 'img').get_attribute('src')
    describe = card.find_element(By.CSS_SELECTOR, "div[data-cy='ad-card-title']").find_element(By.TAG_NAME, 'h6').text

    try:
        state_tag = card.find_element(By.CSS_SELECTOR, "span[class='css-3lkihg']").get_attribute('title')
    except Exception as er:
        print(er)
        state_tag = ''

    location_date = card.find_element(By.CSS_SELECTOR, "p[data-testid='location-date']").text
    describe_link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')

    try:
        price = card.find_element(By.CSS_SELECTOR, "p[data-testid='ad-price']").text.replace(" ", "")
        if int(price.replace("грн.", "").split('\n')[0]) <= int(max_price):
            add_price = price
        else:
            return None, None
    except Exception as er:
        print(er)
        add_price = 'Ціна не вказана'

    card_to_file.append([f"id={id2}, {image_link}, {describe}, {state_tag}, {add_price}, {location_date}, {describe_link}"])

    return f"{image_link}, {describe}, {state_tag}, {add_price}, {location_date}", describe_link



def scroll(item):
    driver.execute_script("arguments[0].scrollIntoView(true);", item)


def get_contacts(link):
    driver.get(link)
    driver.implicitly_wait(20)
    contacts = driver.find_element(By.XPATH, "//button[text()='показати']")
    time.sleep(4)
    driver.execute_script("arguments[0].scrollIntoView({behavior:\"auto\", block:\"center\", inline:\"center\"});", contacts)
    time.sleep(4)
    contacts.click()
    time.sleep(4)
    tel = driver.find_element(By.CSS_SELECTOR, "a[data-testid='contact-phone']").text
    print('tel = ', tel)
    return tel

