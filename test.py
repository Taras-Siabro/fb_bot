
import os
import json
import time
import random
import platform
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.common.keys import Keys
import pyperclip
import config
from fake_useragent import UserAgent

class FBBot:
    def __init__(self):
        self.COOKIES_FILE = str(Path(__file__).parent / 'facebook_cookies.json')
        self.ua = UserAgent()  # Инициализация UserAgent
        self.driver = self.setup_driver()
        self.logged_in = False

    def setup_driver(self):
        chrome_options = Options()
        
        # Настройки для антидетекта
        
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-mobile-emulation")
        # Параметры окна
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Рандомизация геолокации
        chrome_options.add_argument("--disable-geolocation")
        
        # Отключение автоматизации
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Настройки для Linux
        if platform.system() == 'Linux':
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service("drivers/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        

        
        return driver

    def random_delay(self, min_sec, max_sec=None):
        if max_sec is None:
            max_sec = min_sec * 1.5
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def accept_cookies(self):
        try:
            time.sleep(5)
            cookie_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
            "//div[@aria-label='Allow all cookies' and not(@aria-disabled='true')]"))  # Fixed XPath syntax
            )

        # Triple-click strategy for maximum reliability
            try:
                cookie_btn.click()  # Normal click first
            except:
                self.driver.execute_script("arguments[0].click();", cookie_btn)
            return True
        except Exception as e:
            print(f"Не удалось принять куки: {str(e)}")
            return False

    def human_like_click(self, element):
        try:
            action = ActionChains(self.driver)
            action.move_to_element(element).pause(random.uniform(0.1, 0.3)).click().perform()
        except:
            self.driver.execute_script("arguments[0].click();", element)

    def human_like_type(self, element, text):
        for char in text:
            element.send_keys(char)
            self.random_delay(0.1, 0.3)
        self.random_delay(0.5, 1.5)

    def save_cookies(self):
        try:
            cookies = self.driver.get_cookies()
            with open(self.COOKIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=4)
            print(f"Cookies успешно сохранены в {self.COOKIES_FILE}")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении cookies: {str(e)}")
            return False

    def load_cookies(self):
        try:
            if not os.path.exists(self.COOKIES_FILE):
                print(f"Файл cookies не найден: {self.COOKIES_FILE}")
                return False
                
            with open(self.COOKIES_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            self.driver.get("https://facebook.com")
            self.random_delay(3, 5)
            self.driver.delete_all_cookies()
            
            for cookie in cookies:
                if 'domain' in cookie and 'facebook.com' not in cookie['domain']:
                    cookie['domain'] = '.facebook.com'
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Не удалось добавить cookie: {str(e)}")
                    continue
            
            print("Cookies успешно загружены")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке cookies: {str(e)}")
            return False

    def is_logged_in(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, 
                '//a[contains(@href, "profile.php") or contains(@aria-label, "Profile") or contains(@aria-label, "Профиль") or contains(@aria-label, "Профіль")]'))
            )
            self.logged_in = True
            return True
        except:
            try:
                menu = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Account" or @aria-label="Аккаунт" or @aria-label="Обліковий запис"]'))
                )
                self.logged_in = True
                return True
            except:
                self.logged_in = False
                return False

    def login(self):
        try:
            self.driver.get("https://facebook.com")
            self.random_delay(3, 6)

            self.accept_cookies()
            self.random_delay(2, 4)
            
            # Вводим email
            email_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.clear()
            self.human_like_type(email_field, config.FB_EMAIL)
            
            # Вводим пароль
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.clear()
            self.human_like_type(password_field, config.FB_PASSWORD)
            
            # Нажимаем кнопку входа
            login_button = self.driver.find_element(By.NAME, "login")
            self.human_like_click(login_button)
            self.random_delay(5, 8)
            
            # Проверка двухфакторной аутентификации
            try:
                code_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "approvals_code"))
                )
                print("Требуется двухфакторная аутентификация. Введите код вручную.")
                input("После ввода кода нажмите Enter в консоли...")
                self.random_delay(3, 5)
            except:
                pass
            
            if self.is_logged_in():
                print("Вход выполнен успешно")
                return True
            else:
                print("Проверяем возможные ошибки...")
                try:
                    error = self.driver.find_element(By.XPATH, '//div[contains(text(), "incorrect") or contains(text(), "неверный") or contains(text(), "невірний")]')
                    print(f"Ошибка входа: {error.text}")
                except:
                    print("Неизвестная ошибка входа")
                return False
            
        except Exception as e:
            print(f"Ошибка при входе: {str(e)}")
            return False

    def join_group(self, group_url):
        """Join a group if not already a member"""
        try:
            print(f"Processing group: {group_url}")
            self.driver.get(group_url)
            self.random_delay(4, 6)
            
            # Check if already a member
            try:
                # Multiple ways to check membership
                member_indicator = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, 
                    "//div[@aria-label='Joined' or "
                    "//div[contains(., 'Member') or "
                    "//div[contains(., 'Invite') or "
                    "//div[contains(., 'You joined')]"))
                )
                print(f"Already a member of group: {group_url}")
                return True
            except:
                pass
            
            # Try different ways to find join button
            join_button = None
            
            # Method 1: By aria-label
            try:
                join_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, 
                    "//div[@role='button' and contains(@aria-label, 'Join group')]"))
                )
            except:
                pass
            
            # Method 2: By button text
            if not join_button:
                try:
                    join_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, 
                        "//div[contains(., 'Join Group') and @role='button']"))
                    )
                except:
                    pass
            
            # Method 3: By span text inside button
            if not join_button:
                try:
                    join_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, 
                        "//span[contains(., 'Join Group')]/ancestor::div[@role='button']"))
                    )
                except:
                    pass
            
            
                
                # Handle confirmation dialogs
                try:
                    confirm_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, 
                        "//div[@role='button' and (contains(., 'Confirm') or contains(., 'Join Group'))]"))
                    )
                    self.human_like_click(confirm_button)
                    print("Confirmed join request")
                except:
                    pass
                
                # Check if join was successful
                self.random_delay(2, 4)
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, 
                        "//div[contains(., 'Requested') or contains(., 'Pending') or contains(., 'Joined')]"))
                    )
                    print(f"Successfully joined or requested to join group: {group_url}")
                    return True
                except:
                    print("Join action performed but success not confirmed")
                    return True
            else:
                # Take screenshot for debugging
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                self.driver.save_screenshot(f"join_error_{timestamp}.png")
                print(f"Join button not found for group: {group_url}")
                print("Screenshot saved for debugging")
                return False
                
        except Exception as e:
            print(f"Error joining group {group_url}: {str(e)}")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            self.driver.save_screenshot(f"join_error_{timestamp}.png")
            return False

    def post_to_group(self, group_url):
        """Публикует сообщение в группе, если состоит в ней"""
        try:
            self.driver.get(group_url)
            self.random_delay(5, 10)
            
            # Проверяем, состоит ли в группе
            # try:
            #     # Если видим кнопку "Joined" или "Вы участник", значит в группе
            #     WebDriverWait(self.driver, 5).until(
            #         EC.presence_of_element_located((By.XPATH, 
            #         "//div[@aria-label='Joined' or @aria-label='Вы участник' or @aria-label='Ви учасник']"))
            #     )
            # except:
            #     print(f"Не состоим в группе: {group_url}")
            #     return False
            
            # Пытаемся опубликовать
            try:
                post_box = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, 
                    "//div[contains(@class, 'xi81zsa')]//span[contains(., 'Write something') or contains(., 'Написать пост') or contains(., 'Написати допис')]"))
                )
                self.human_like_click(post_box)
            except:
                print("Не удалось найти поле для ввода сообщения")
                return False
            
            self.random_delay(3, 6)
            
            text = random.choice(config.MESSAGES)
            pyperclip.copy(text)
            
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            self.random_delay(2, 4)
            
            post_button = WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, 
                "//div[@role='button' and (@aria-label='Post' or @aria-label='Опубликовать' or @aria-label='Опублікувати')]"))
            )
            self.human_like_click(post_button)
            
            print(f"Сообщение опубликовано в группе {group_url}")
            return True
        except Exception as e:
            print(f"Ошибка при публикации в группе {group_url}: {str(e)}")
            return False

    def process_groups(self):
        # """Обрабатывает все группы: вступает и публикует"""
        # if not self.logged_in:
        #     print("Не выполнен вход, обработка групп невозможна")
        #     return False
        
        # # Сначала вступаем во все группы
        # print("\n=== Вступление в группы ===")
        # for i, group in enumerate(config.GROUPS):
        #     print(f"[{i+1}/{len(config.GROUPS)}] Обработка группы: {group}")
        #     self.join_group(group)
        #     delay = random.randint(5, 8)
            
        #     time.sleep(delay)
            
                
        #     # Задержка между обработкой групп
        #     if i < len(config.GROUPS) - 1:
        #         delay = random.randint(7, 15)  # 30-90 секунд между группами
        #         print(f"Ожидание {delay} секунд перед следующей группой...")
        #         time.sleep(delay)
        
        # Затем публикуем во всех группах
        print("\n=== Публикация в группах ===")
        for i, group in enumerate(config.GROUPS):
            print(f"[{i+1}/{len(config.GROUPS)}] Публикация в группе: {group}")
            self.post_to_group(group)
            
            # Увеличенная задержка между публикациями
            if i < len(config.GROUPS) - 1:
                delay = random.randint(15, 25)  # 2-5 минут между публикациями
                print(f"Ожидание {delay} секунд перед следующей публикацией...")
                time.sleep(delay)
        
        return True

    def run(self):
        try:
            self.login()
            while True:
                time.sleep(1800)
                self.process_groups()
                
            
        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
        finally:
            input("Нажмите Enter для завершения...")
            self.driver.quit()

if __name__ == "__main__":
    bot = FBBot()
    bot.run()