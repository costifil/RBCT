'''
breeze module
Read text from breezetranslate.com and push it into a queue
'''
from threading import Thread, Event
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Breeze(Thread):
    '''
    Breeze class: read from breezetranslate web page and add to the queue
    '''

    def __init__(self, write_queue, **kwargs):
        super().__init__(name="Breeze_Thrd")

        self.url = kwargs.get("BreezeTranslate", {}).get("url")
        if not self.url:
            raise Exception("Missing URL in the cfg.json file")

        self.language = kwargs.get("BreezeTranslate", {}).get("language")
        if not self.language:
            raise Exception("Missing language in the cfg.json file")

        self.url = self.url + self.language
        self.max_lines = int(kwargs.get("BreezeTranslate", {}).get("max_subtitle_lines", 2))

        self.write_q = write_queue

        self.stop_process = Event()
        self.driver = None
        self.projector_obj = None

    def set_projector_obj(self, projector):
        '''set the projector object'''
        self.projector_obj = projector

    def stop(self):
        '''stop the thread'''
        self.stop_process.set()
        time.sleep(0.2)
        self.driver.quit()
        logging.info("%s stopped!", self.name)

    def stop_if_req(self, driver):
        '''stop the wait.until method from selenium'''
        if self.stop_process.is_set():
            raise TimeoutException("Stop requested")
        return False

    def run(self):
        logging.info("Breeze started ...")
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

        while not self.stop_process.is_set():
            logging.info("Wait for driver...")

            wait = WebDriverWait(self.driver, 30)

            used_text: list[str] = []
            while not self.stop_process.is_set():
                try:
                    web_text: list[str] = []
                    used_text = used_text[-20:]

                    elements = wait.until(lambda d: self.stop_if_req(d) or EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, f"p.font-bold[lang='{self.language}']"))(d))

                    for elm in elements[-10:]: # get the last 10 elements
                        web_text.append(elm.text)

                    for text in web_text:
                        if text in used_text:
                            logging.debug("Text already in the used list: %s", text)
                            continue

                        self.write_q.add(text)
                        used_text.append(text)
                        logging.debug("Text added to the queue: %s", text)

                except TimeoutException:
                    logging.warning("Timed out")

                except Exception as ex:
                    self.stop_process.set()
                    logging.error("General exception: %s\n%s", self.stop_process.is_set(), ex)

                if self.stop_process.is_set():
                    break

                time.sleep(0.5)
