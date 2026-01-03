'''
consumer module
Read text from queue and send it to the OBS
'''
from threading import Thread, Event
import time
import logging
import queue
from enum import Enum
from obswebsocket import obsws, requests

class LenText(Enum):
    '''
    Enum with the length of a text as first value and
    the seconds to stay on the screen in OBS as the second value
    '''
    LESS_1 = (20, 1)    # 20 -> 1
    LESS_2 = (40, 2)    # 40 -> 2
    LESS_3 = (90, 3)    # 90 -> 3
    LESS_4 = (130, 4)   # 130 -> 4
    LESS_5 = (170, 5)   # 170 -> 5
    LESS_6 = (999, 6)   # any -> 6

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Consumer(Thread):
    '''
    Consumer class: read text from queue and send it to OBS
    '''
    def __init__(self, read_queue, **kwargs):
        super().__init__(name="OBS_Thrd")

        self.host = kwargs.get("OBS", {}).get("host")
        self.port = kwargs.get("OBS", {}).get("port")
        self.password = kwargs.get("OBS", {}).get("password")
        self.gdi_text = kwargs.get("OBS", {}).get("gdi_text")

        self.read_q = read_queue
        self.stop_process = Event()
        self.ws_obs = None

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
        if self.ws_obs:
            # sending empty string to GDI text in OBS
            self.ws_obs.call(requests.SetInputSettings(inputName=self.gdi_text,
                                                       inputSettings={"text": ""},
                                                       overlay=True))
        self.stop_process.set()
        self.disconnect_obs()
        logging.info("%s stopped!", self.name)

    def run(self):
        logging.info("Consumer started ...")
        self.connect_obs()

        t_on_s = 1
        while not self.stop_process.is_set():
            try:
                text = self.read_q.pop()
                if text:
                    len_text = len(text)
                    if len_text <= LenText.LESS_1.x:
                        t_on_s = LenText.LESS_1.y
                    elif len_text <= LenText.LESS_2.x:
                        t_on_s = LenText.LESS_2.y
                    elif len_text <= LenText.LESS_3.x:
                        t_on_s = LenText.LESS_3.y
                    elif len_text <= LenText.LESS_4.x:
                        t_on_s = LenText.LESS_4.y
                    elif len_text <= LenText.LESS_5.x:
                        t_on_s = LenText.LESS_5.y
                    else:
                        t_on_s = LenText.LESS_6.y

                    logging.debug("Text read from the queue: %s", text)
                    #print(text)

                    self.ws_obs.call(requests.SetInputSettings(inputName=self.gdi_text,
                                                               inputSettings={"text": text},
                                                               overlay=True))
                else:
                    t_on_s = 0.3

            except queue.Empty:
                logging.error("queue.Empty")
                continue
            except IndexError as ex:
                logging.error("IndexError: %s", ex)
                continue

            time.sleep(t_on_s)
