import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.common.keys import Keys
import pyperclip
import config

class FBBot:
    def __init__(self):
        self.driver = self.setup_driver()  # Настраиваем браузер

    def setup_driver(self):
        chrome_options = Options()
        
        # Параметры Chrome
        chrome_options.add_argument("--disable-notifications")  # Отключаем уведомления
        chrome_options.add_argument("--start-maximized")       # Открываем на весь экран
        
        # Скрываем автоматизацию
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Указываем путь к драйверу
        service = Service("drivers/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def accept_cookies(self):
        cookie_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
            "//div[@aria-label='Allow all cookies' and not(@aria-disabled='true')]"))  # Fixed XPath syntax
        )

        # Triple-click strategy for maximum reliability
        try:
            cookie_btn.click()  # Normal click first
        except:
            self.driver.execute_script("arguments[0].click();", cookie_btn)  # JS click fallback
        # finally:
        #     ActionChains(self.driver).move_to_element(cookie_btn).click().perform()  # Force click

    def post_message(self):
        
        for group in config.GROUPS:
            self.driver.get(group)
            time.sleep(5)
            
            wait = WebDriverWait(self.driver, 5)
            button = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//span[text()='Write something...']/ancestor::div[contains(@class, 'xi81zsa')]"
            )))
            button.click()
            time.sleep(2)
            # text_area = wait.until(EC.presence_of_element_located((
            #     By.XPATH,
            #     "//div[@role='textbox' and @contenteditable='true']"
            # )))
            # text_area.click()
            

            text = "Test message"
            
            pyperclip.copy(text)  #

            time.sleep(1)

            from selenium.webdriver.common.action_chains import ActionChains

            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            
            time.sleep(3)

            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Post']"))
            )
            post_button.click()
            time.sleep(5)


    def login(self):

        self.driver.get("https://facebook.com")
        time.sleep(3)

        self.accept_cookies()
        time.sleep(10)
        email_field = self.driver.find_element(By.ID, "email")
        email_field.send_keys(config.FB_EMAIL) 
        
        password_field = self.driver.find_element(By.ID, "pass")
        password_field.send_keys(config.FB_PASSWORD)
        
       
        login_button = self.driver.find_element(By.NAME, "login")
        login_button.click()
        time.sleep(5)

    def run(self):
        
        self.login() 
        time.sleep(5)

        self.post_message()
        time.sleep(3600)
        
while True:
    if __name__ == "__main__":
        bot = FBBot()
        bot.run() 