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
from selenium.common.exceptions import TimeoutException
from obswebsocket import obsws, requests
from ch_utils import ch_utils as util       # pylint: disable=import-error


def worker(stop_event: Event, data: dict, obs_socket, driver):
    '''
    worker threaded function to read the translation from web page (breezetranslate.com)
    - text read from the web page is pushed to web_text list
    - text that was already sent to OBS will be pushed into used_text list
    - text from web_text list that does not exists in the used_text list
        will be pushed to remaining_test list to be sent to the OBS
    - Maximum 2 items from remaining_text list will be sent to OBS
    '''
    language = data.get("language", "ro")
    max_lines = int(data.get("max_subtitle_lines", 2))

    print("Worker started ...")
    while not stop_event.is_set():
        print("Wait for driver...")
        wait = WebDriverWait(driver, 30)

        web_text: list[str]  =[]
        used_text: list[str] = []
        print_count = 0
        while not stop_event.is_set():
            try:
                print_count += 1
                web_text = []
                used_text = used_text[-20:]
                remaining_text: list[str] = []
                elements = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, f"p.font-bold[lang='{language}']")))


                for elm in elements[-10:]: # get the last 20 elements
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
                        # obs_socket.call(requests.SetInputSettings(inputName="MyTextSource",
                                                                  # inputSettings={"text": txt},
                                                                  # overlay=True))
                        print(txt)
                        used_text.append(txt)
                        count = count - 1
                if len(remaining_text) > 0:
                    print()

            except TimeoutException:
                # should send an empty string to OBS to clear the subtitle
                print("Timed out - retry")

            except Exception as ex:
                print("General exception:\n", ex)

            if stop_event.is_set():
                break

            time.sleep(1)

def connect_OBS(cfg_info):

    ws = obsws(cfg_info.get("host"),
               cfg_info.get("port"),
               cfg_info.get("password"))
    ws.connect()

    return ws

def disconnect_OBS(web_sock):
    if web_sock:
        web_sock.disconnect()

def main():
    '''
    main function
    '''
    data = util.get_config_info()
    for item in data:
        if item.get("application") == "translate_subtitle_OBS":
            data = item
            break
    url = data.get("url") + data.get("language")
    if not url:
        raise Exception("Missing URL in the cfg.json file")

    stop_event = Event()

    obs_web_socket = None
    #obs_web_socket = connect_OBS(data)

    driver = webdriver.Chrome()
    driver.get(url)
    thrd = Thread(target=worker, args=(stop_event,
                                       data,
                                       obs_web_socket,
                                       driver,))
    thrd.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()

    thrd.join()

    disconnect_OBS(obs_web_socket)
    driver.quit()

    print("Done!")

if __name__ == "__main__":
    main()
