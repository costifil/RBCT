'''
producer module
Read text from breezetranslate.com and push it into a queue
'''
from threading import Thread, Event
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Producer(Thread):
    '''
    Producer class: read from breezetranslate web page and add to the queue
    '''

    def __init__(self, write_queue, **kwargs):
        super().__init__()

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

        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

    def stop(self):
        '''stop the thread'''
        self.stop_process.set()
        self.driver.quit()

    def run(self):
        logging.info("Producer started ...")

        while not self.stop_process.is_set():
            logging.info("Wait for driver...")
            wait = WebDriverWait(self.driver, 30)

            used_text: list[str] = []
            while not self.stop_process.is_set():
                try:
                    web_text: list[str] = []
                    used_text = used_text[-20:]

                    elements = wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, f"p.font-bold[lang='{self.language}']")))

                    for elm in elements[-10:]: # get the last 10 elements
                        #if elm.text in web_text:
                        #    continue
                        web_text.append(elm.text)

                    for text in web_text:
                        if text in used_text:
                            logging.debug("Text already in the used list: %s", text)
                            continue
                        self.write_q.put(text)
                        used_text.append(text)
                        logging.debug("Text added to the queue: %s", text)

                except TimeoutException:
                    print("Timed out")
                    logging.error("Timed out")

                except Exception as ex:
                    logging.error("General exception:\n%s", ex)

                if self.stop_process.is_set():
                    break

                time.sleep(0.5)
