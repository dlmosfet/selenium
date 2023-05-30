from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ddddocr
import time
import base64


class NKUSTLogin:
    def __init__(self, chrome_driver_path):
        self.chrome_driver_path = chrome_driver_path
        self.driver = None
        self.ocr = ddddocr.DdddOcr()

    def setup_driver(self):
        service = Service(self.chrome_driver_path)
        self.driver = webdriver.Chrome(service=service)

    def login(self):
        self.driver.get('https://webap.nkust.edu.tw/nkust/')
        time.sleep(2)

        wait = WebDriverWait(self.driver, 20)
        iframe = wait.until(EC.presence_of_element_located((By.XPATH, '//iframe[@name="mainFrame"]')))
        self.driver.switch_to.frame(iframe)

        img_base64 = self.driver.execute_script("""
            var ele = arguments[0];
            var cnv = document.createElement('canvas');
            cnv.width = ele.width; cnv.height = ele.height;
            cnv.getContext('2d').drawImage(ele, 0, 0);
            return cnv.toDataURL('image/jpeg').substring(22);    
            """, self.driver.find_element(By.XPATH, "//*[//*[@id='verifyCode']]/img"))



        with open('captcha_login.png', 'rb') as image:
            img_bytes = image.read(base64.b64decode(img_base64))
        res = self.ocr.classification(img_bytes)

        stuid = self.driver.find_element(By.CSS_SELECTOR, 'input[name="uid"]')
        password = self.driver.find_element(By.CSS_SELECTOR, 'input[name="pwd"]')
        code = self.driver.find_element(By.CSS_SELECTOR, 'input[name="etxt_code"]')

        stuid.send_keys('stu')
        password.send_keys('pwd')
        code.send_keys(res)

        self.driver.find_element(By.CSS_SELECTOR, 'input[name="chk"]').click()

        self.driver.switch_to.default_content()


    def close(self):
        if self.driver:
            self.driver.quit()


if __name__ == '__main__':
    chrome_driver_path = "./goolemapSpider/chromedriver.exe"
    nkust_login = NKUSTLogin(chrome_driver_path)
    try:
        nkust_login.setup_driver()
        nkust_login.login()
    except Exception as e:
        print("发生错误：", str(e))
    finally:
        nkust_login.close()
