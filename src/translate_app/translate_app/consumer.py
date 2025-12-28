'''
consumer module
Read text from queue and send it to the OBS
'''
from threading import Thread, Event
import time
import logging
import queue
from obswebsocket import obsws, requests

class Consumer(Thread):
    '''
    Consumer class: read text from queue and send it to OBS
    '''
    def __init__(self, read_queue, **kwargs):
        super().__init__()

        self.host = kwargs.get("OBS", {}).get("host")
        self.port = kwargs.get("OBS", {}).get("port")
        self.password = kwargs.get("OBS", {}).get("password")
        self.gdi_text = kwargs.get("OBS", {}).get("gdi_text")

        self.read_q = read_queue
        self.stop_process = Event()
        self.ws_obs = None
        self.connect_obs()

    def connect_obs(self):
        '''connect to OBS'''
        self.ws_obs = obsws(self.host, self.port, self.password)
        if self.ws_obs:
            self.ws_obs.connect()
        else:
            logging.error("Fail to get OBS socket")
            raise Exception("Fail to get OBS socket")
        logging.info("Connected to OBS!")

    def disconnect_obs(self):
        '''disconnect from OBS'''
        if self.ws_obs:
            self.ws_obs.disconnect()

    def stop(self):
        '''stop the thread'''
        self.stop_process.set()
        self.disconnect_obs()

    def run(self):
        logging.info("Consumer started ...")
        print("Consumer started")

        ts = 1
        while not self.stop_process.is_set():
            try:
                text = self.read_q.pop()
                if text:
                    len_txt = len(text)
                    if len_txt > 140:
                        ts = 5
                    elif len_txt > 100:
                        ts = 4
                    elif len_txt > 40:
                        ts = 3
                    elif len_txt > 20:
                        ts = 2
                    else:
                        ts = 1

                    logging.debug("Text read from the queue: %s", text)
                    print(text)

                    self.ws_obs.call(requests.SetInputSettings(inputName=self.gdi_text,
                                                               inputSettings={"text": text},
                                                               overlay=True))
                else:
                    ts = 0.5

            except queue.Empty:
                logging.error("queue.Empty")
                continue
            except IndexError as ex:
                logging.error("IndexError: %s", ex)
                continue

            time.sleep(ts)
