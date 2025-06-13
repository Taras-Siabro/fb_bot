import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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
        service = Service("drivers/chromedriver.exe")
        return webdriver.Chrome(service=service, options=chrome_options)

    def login(self):
        self.driver.get("https://facebook.com")
        time.sleep(2)
        
        email_field = self.driver.find_element(By.ID, "email")
        email_field.send_keys(config.FB_EMAIL)  # Берем email из config.py
        
        password_field = self.driver.find_element(By.ID, "pass")
        password_field.send_keys(config.FB_PASSWORD)
        
        # Клик по кнопке входа
        login_button = self.driver.find_element(By.NAME, "login")
        login_button.click()
        time.sleep(5)

    def run(self):
        self.login()  # Теперь login() без аргументов
        
        for group_url in config.GROUPS:  # Берем группы из config.py
            message = random.choice(config.MESSAGES)  # Берем сообщения из config.py
            success = self.post_message(group_url, message)
            print(f"Группа: {group_url} | Статус: {'Успех' if success else 'Провал'}")
            time.sleep(30)

if __name__ == "__main__":
    bot = FBBot()
    bot.run()  # Теперь без передачи параметров