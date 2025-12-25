'''
module to read text from breezetranslate.com and send it to OBS
as subtitle for online streaming
'''

from threading import Thread, Event
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ch_utils import ch_utils as util       # pylint: disable=import-error


def worker(stop_event: Event, language: str, max_lines: int, driver):
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
                elements = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, f"p.font-bold[lang='{language}']")))
                for elm in elements:
                    if elm.text in web_text:
                        continue
                    web_text.append(elm.text)
                for item in web_text:
                    if item in used_text:
                        continue
                    remaining_text.append(item)
                count = max_lines
                for txt in remaining_text:
                    if count > 0:
                        print(txt)
                        used_text.append(txt)
                        count = count - 1

            except Exception as ex:
                print("Genral exception:\n", ex)

            if stop_event.is_set():
                break

            time.sleep(1)

def main():
    '''
    main function
    '''
    data = util.get_config_info()
    for item in data:
        if item.get("application") == "translate_subtitle_OBS":
            data = item
            break
    url = data.get("url")
    if not url:
        raise Exception("Missing URL in the cfg.json file")

    stop_event = Event()

    driver = webdriver.Chrome()
    driver.get(url)
    thrd = Thread(target=worker, args=(stop_event,
                                       data.get("language", "ro"),
                                       int(data.get("max_subtitle_lines", 2)),
                                       driver,))
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
