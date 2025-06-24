from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import URL


def run_driver(browser: str) -> webdriver:
    """
    Function to initialize and run the WebDriver for different browsers.
    Arguments:
    - browser: str (chrome, edge, firefox)

    Returns:
    - driver: selenium.webdriver
    """
    driver = None
    if browser == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
    elif browser == 'edge':
        driver = webdriver.Edge()
        driver.maximize_window()
    elif browser == 'firefox':
        driver = webdriver.Firefox()
        driver.maximize_window()
    if driver:
        driver.get(URL)
        driver.implicitly_wait(20)
    return driver


def choice_things(driver: webdriver, thing: str, region: str, location: str):
    """
    Interacts with the search field and selects region and location.
    Arguments:
    - driver: selenium.webdriver
    - thing: str (search query)
    - region: str (region to select)
    - location: str (city or area to select)

    Returns:
    - cards: list (list of WebElements representing items)
    """
    wait = WebDriverWait(driver, 20)
    try:
        # Type in the search field
        thing_to_search = wait.until(EC.presence_of_element_located((By.ID, "search")))
        thing_to_search.send_keys(thing)

        # Open region selector
        wait.until(EC.element_to_be_clickable((By.ID, "location-input"))).click()

        # Select region
        reg1 = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{region} область']/parent::div/parent::li")))
        driver.execute_script("arguments[0].scrollIntoView({behavior:'auto', block:'center'});", reg1)
        reg1.click()

        # Select city or area
        if location == 'область':
            reg2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-cy= 'all-cities']")))
        else:
            reg2 = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[text()='{location}']")))

        driver.execute_script("arguments[0].scrollIntoView({behavior:'auto', block:'center'});", reg2)
        reg2.click()

        # Click the search button
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="searchBtn"]'))).click()

        # Wait for cards to load
        cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-cy= 'l-card']")))
        return cards

    except Exception as e:
        print(f"Error while interacting with search: {e}")
        return []  # Return an empty list in case of failure

def get_things(id2: int, max_price: str, card):
    """
    Extracts necessary details from each card element.
    Arguments:
    - id2: int (unique ID for the item)
    - max_price: str (maximum price for filtering items)
    - card: selenium.webdriver.remote.webelement.WebElement (the card to extract data from)

    Returns:
    - tuple: (card_id, description, card_link)
    """
    card_id = card.get_attribute('id')
    image_link = card.find_element(By.TAG_NAME, 'img').get_attribute('src')
    describe = card.find_element(By.CSS_SELECTOR, "div[data-cy='ad-card-title']").find_element(By.TAG_NAME, 'h6').text

    try:
        price = card.find_element(By.CSS_SELECTOR, "p[data-testid='ad-price']").text
        price_digits = ''.join(filter(str.isdigit, price))
        if price_digits and int(price_digits) <= int(max_price):
            add_price = price
        else:
            return None, None, None
    except Exception as er:
        print('price error: ', er)
        add_price = 'Ціна не вказана'

    try:
        state_tag = card.find_element(By.CSS_SELECTOR, "span[class='css-3lkihg']").get_attribute('title')
    except Exception as er:
        print("state_tag error: ", er)
        state_tag = ''

    location_date = card.find_element(By.CSS_SELECTOR, "p[data-testid='location-date']").text
    describe_link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')

    return card_id, f"id={id2}, {image_link}, {describe}, {state_tag}, {add_price}, {location_date}", describe_link


def scroll(driver: webdriver, item: webdriver):
    """
    Scrolls the page to bring a particular element into view.
    Arguments:
    - driver: selenium.webdriver
    - item: selenium.webdriver.remote.webelement.WebElement (the item to scroll to)
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
    except Exception as err:
        print('scroll error: ', err)


def get_contacts(link: str, driver: webdriver) -> str:
    """
    Extracts the contact information (phone number) from a card's detail page.
    Arguments:
    - link: str (URL to open for detailed view)
    - driver: selenium.webdriver

    Returns:
    - str: phone number or a fallback message if not found
    """
    driver.get(link)
    wait = WebDriverWait(driver, 20)

    try:
        # Wait for the 'показати' button to appear and be clickable
        contacts_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='показати']")))

        # Scroll to the button
        driver.execute_script("arguments[0].scrollIntoView({behavior:'auto', block:'center'});", contacts_btn)

        # Wait for stability, then click
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='показати']"))).click()

        # Wait for the phone number to appear
        phone_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a[data-testid='contact-phone']")))
        return phone_element.text

    except Exception as er:
        print('phone error:', er)
        return "На жаль телефон не знайдено"
