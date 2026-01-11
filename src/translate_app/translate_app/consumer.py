'''
consumer module
Read text from queue and send it to the OBS
'''
from threading import Thread, Event
import time
import logging
import queue
from enum import Enum
from obswebsocket import obsws, requests    # pylint: disable=import-error

class LenText(Enum):
    '''
    Enum with the length of a text as first value and
    the seconds to stay on the screen in OBS as the second value
    '''
    LESS_1 = (20, 1)    # 20 -> 1
    LESS_2 = (40, 2)    # 40 -> 2
    LESS_3 = (75, 3)    # 75 -> 3
    LESS_4 = (110, 4)   # 110 -> 4
    LESS_5 = (155, 5)   # 155 -> 5
    LESS_6 = (999, 6)   # 999 -> 6


class Consumer(Thread):
    '''
    Consumer class: read text from queue and send it to OBS
    '''
    def __init__(self, read_queue, **kwargs):
        super().__init__(name="OBS_Thrd")

        self.credentials = {"host": kwargs.get("OBS", {}).get("host"),
                            "port": kwargs.get("OBS", {}).get("port"),
                            "password": kwargs.get("OBS", {}).get("password")}

        self.gdi_text = kwargs.get("OBS", {}).get("gdi_text")

        self.read_q = read_queue
        self.stop_process = Event()
        self.ws_obs = None
        self.enable_text = kwargs.get("obs_enable")

    def connect_obs(self):
        '''connect to OBS'''
        self.ws_obs = obsws(self.credentials.get("host"),
                            self.credentials.get("port"),
                            self.credentials.get("password"))
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

    def enable_subtitle(self, enable: bool=True):
        '''enable the flag to send text on OBS screen'''
        self.enable_text = enable
        return self.enable_text

    def stop(self):
        '''stop the thread'''
        if self.ws_obs:
            # sending empty string to GDI text in OBS
            self.send_text("")

        self.stop_process.set()
        self.disconnect_obs()
        logging.info("%s stopped!", self.name)

    def send_text(self, text: str):
        '''sending text to OBS'''
        if self.enable_text:
            self.ws_obs.call(requests.SetInputSettings(inputName=self.gdi_text,
                                                       inputSettings={"text": text},
                                                       overlay=True))
        else:
            self.ws_obs.call(requests.SetInputSettings(inputName=self.gdi_text,
                                                       inputSettings={"text": ""},
                                                       overlay=True))

    def run(self):
        logging.info("Consumer started ...")
        self.connect_obs()

        t_on_s = 1
        no_text = 0
        while not self.stop_process.is_set():
            try:
                move_on = False
                text = self.read_q.pop()
                if text:
                    no_text = 0
                    t_on_s = time_on_screen(len(text))
                    if t_on_s == LenText.LESS_6.value[1]:
                        #print("split the sentence")
                        move_on = True
                        new_text_list = []
                        text_list = text.split()
                        half_text = len(text_list) // 2
                        new_text_list.append(" ".join(text_list[:half_text]))
                        new_text_list.append(" ".join(text_list[half_text:]))
                        for item in new_text_list:
                            self.send_text(item)
                            t_on_s = time_on_screen(len(item))
                            time.sleep(t_on_s)

                    logging.debug("Text read from the queue: %s", text)
                    #print(text)

                    if not move_on:
                        self.send_text(text)
                else:
                    no_text += 1
                    t_on_s = 0.2
                    if no_text >= 5:
                        self.send_text("")

            except queue.Empty:
                logging.error("queue.Empty")
                continue
            except IndexError as ex:
                logging.error("IndexError: %s", ex)
                continue

            time.sleep(t_on_s)

def time_on_screen(len_text):
    '''calculate the time to stay on the OBS screen'''
    t_on_s = LenText.LESS_6.value[1]

    if len_text <= LenText.LESS_1.value[0]:
        t_on_s = LenText.LESS_1.value[1]
    elif len_text <= LenText.LESS_2.value[0]:
        t_on_s = LenText.LESS_2.value[1]
    elif len_text <= LenText.LESS_3.value[0]:
        t_on_s = LenText.LESS_3.value[1]
    elif len_text <= LenText.LESS_4.value[0]:
        t_on_s = LenText.LESS_4.value[1]
    elif len_text <= LenText.LESS_5.value[0]:
        t_on_s = LenText.LESS_5.value[1]
    #elif len_text <= LenText.LESS_6.value[0]:
    #    t_on_s = LenText.LESS_6.value[1]

    return t_on_s
