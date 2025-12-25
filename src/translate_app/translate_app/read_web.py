'''
module to read text from breezetranslate.com and send it to OBS
as subtitle for online streaming
'''

from threading import Thread, Event
import time
#import typing
#from typing import Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.chrome.service import Service
from utils import utils as util


def worker(stop_event: Event, driver):
    '''
    worker threaded function to read the translation from web page (breezetranslate.com)
    - text read from the web page is pushed to web_text list
    - text that was already sent to OBS will be pushed into used_text list
    - text from web_text list that does not exists in the used_text list
        will be pushed to remaining_test list to be sent to the OBS
    - Maximum 2 items from remaining_text list will be sent to OBS
    '''
    print("Worker started ...")
    while not stop_event.is_set():
        print("Wait for driver...")
        wait = WebDriverWait(driver, 10)
        web_text: list[str]  =[]
        used_text: list[str] = []
        while not stop_event.is_set():
            try:
                remaining_text: list[str] = []
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                                           "p.font-bold[lang='ro']")
                                                                          ))
                for elm in elements:
                    if elm.text in web_text:
                        continue
                    web_text.append(elm.text)
                for item in web_text:
                    if item in used_text:
                        continue
                    remaining_text.append(item)
                count = 2
                for txt in remaining_text:
                    if count > 0:
                        print(txt)
                        used_text.append(txt)

            except Exception as ex:
                print("Genral exception:\n", ex)
            time.sleep(1)

def main():
    '''
    main function
    '''
    url = "https://bisericabaptistaromanatoronto.breezetranslate.com/client/ro"

    stop_event = Event()

    driver = webdriver.Chrome()
    driver.get(url)
    thrd = Thread(target=worker, args=(stop_event, driver,))
    thrd.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()

    thrd.join()
    driver.quit()
    print("Done!")

if __name__ == "__main__":
    main()
