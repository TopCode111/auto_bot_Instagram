from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager as CM
from datetime import datetime, timedelta

import logging.config
import config
import os
import random
import re
import time

logging.config.fileConfig('logging.config' , disable_existing_loggers=False)
logger = logging.getLogger()

class InstagramBot:
    """Class to define login and like photo methods"""

    def __init__(self,username,password):
        self.logger = logging.getLogger()        
        self.username = username
        self.password = password        
        self.bot = webdriver.Chrome()

    def login(self):
        """User login using credentials"""
        bot = self.bot
        bot.get("https://www.instagram.com/accounts/login/")
        time.sleep(random.randint(2, 3))

        # Click optional "Accept cookies from Instagram on this browser?"
        try:
            bot.find_element(By.CSS_SELECTOR, 'button.aOOlW').click()
            
        except Exception as exp:
            print("No element to click: Accept cookies from Instagram. Skipping..")
        time.sleep(random.randint(2, 3))   

        email = bot.find_element(By.NAME, "username")
        time.sleep(random.randint(1, 2))
        password = bot.find_element(By.NAME, "password")
        email.clear()
        password.clear()
        email.send_keys(self.username)
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)
        time.sleep(random.randint(4, 5))

        # Click optional "Bypass save login info"
        try:
            bot.find_element(By.CSS_SELECTOR, '.cmbtv > button').click()
        except Exception as exp:
            print("No element to click: save login info. Skipping..")

        time.sleep(random.randint(3, 4))
        # Click optional "Turn on Notification"
        try:
            bot.find_element(
                By.CSS_SELECTOR, '.mt3GC > button:last-of-type').click()
            time.sleep(random.randint(3, 4))
        except Exception as exp:
            print("No element to click: Turn on Notification. Skipping..")

    def remove_pop(self):
        closeButton = self.bot.find_element(By.XPATH, "//button[contains(text(),'後で')]")
        closeButton.click()
        time.sleep(random.randint(2, 3))
    
    def like_posts(self, hashtag):
        """Search hashtag URL and like first 50 posts"""
        time.sleep(random.randint(5, 7))
        count = 0
        notLikeCounter = 0
        alreadyLikeCounter  = 0
        bot = self.bot
        bot.get("https://www.instagram.com/explore/tags/" + hashtag)
        time.sleep(random.randint(3, 4))

        # simulate scroll for lazy loading
        for i in range(3):
            bot.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1+i)

        # Get all links, which will be later cleaned for the posts
        links = bot.find_elements(By.XPATH, "//div/a")
        links_hrefs = []
        for link in links:
            # if links have href tag, add it to the list
            try:
                links_hrefs.append(link.get_attribute('href'))
            except Exception as unhandled_exception:
                pass
        
        for i in range(random.randint(4, 5)):
            image = random.choice(links_hrefs)
            try:
                # Check if the links contains posts
                val = re.search(r'^https://www\.instagram\.com/p/', image)
                bot.get(val.string)

                # random sleep between 1 - 3 secs for any 'unusual activity'
                time.sleep(random.randint(5, 10))
                if random.randint(1, 6) % 5 == 0:
                    notLikeCounter += 1
                    self.logger.info('not to try press like_{}'.format(notLikeCounter))
                    print("not to try press like_{}".format(notLikeCounter))
                    time.sleep(random.randint(2, 4))
                else:
                    # いいね
                    bot.set_page_load_timeout(100)                    
                    heart = bot.find_element(By.CSS_SELECTOR, '._aamu > span._aamw > button > div._abm0 > span > svg')
                    # 既にいいねしている場合は、いいねボタンを押さない
                    if heart.get_attribute("aria-label") == '「いいね！」を取り消す' :
                        alreadyLikeCounter += 1
                        self.logger.info('Already Liked!_{}'.format(alreadyLikeCounter))
                        print("already Liked!")
                        pass
                    else:                        
                        bot.find_element(By.CSS_SELECTOR, '._aamu button').click()
                        count += 1
                    
                    time.sleep(random.randint(5, 10))
                
            except Exception as unhandled_exception:
                print("error_{}".format(i))
                time.sleep(random.randint(2, 3))
                
        self.logger.info('liked {} posts'.format(count))
        print("liked {} posts".format(count))
        
    
    def close(self):
        self.bot.quit()
        
    def save_screenshot(self,errorCount):
        screenShotFileName = '{}errorImage{}.png'.format(datetime.now().strftime("%Y%m%d_%H%M%S") , errorCount)
        screenShotFloderPath = os.path.dirname(os.path.abspath(__file__))
        screenShotFullPath = os.path.join(screenShotFloderPath, screenShotFileName)
        self.bot.save_screenshot(screenShotFullPath)


def main(taglist):
    """Main function to like posts"""
    loopCount = 0
    errorCount = 0
    
    email = config.email
    password = config.password
    
    try:
        USER = InstagramBot(email,password)
        USER.login()
        USER.remove_pop()
    except Exception as e:
        quit()
       
    while True:
        try:
            loopCount += 1
            logging.info('Loop Count_{}'.format(loopCount))
            hashtag = random.choice(taglist)
            USER.like_posts(hashtag)
            dt = datetime.now() + timedelta(minutes=random.choice([10, 20, 30, 40, 50]))
            time.sleep(2)
            while datetime.now() < dt:
                time.sleep(1)
            print('Starting next set')
        except Exception as e:
            errorCount += 1
            USER.save_screenshot(errorCount) 
            USER.close()

if __name__ == "__main__":
    
    with open(r'data/tags.txt', 'r',encoding='utf-8') as f:
        taglist = [line.strip() for line in f]
        
    logging.info('Start!!!')
    main(taglist)