'''
obs module
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

class Obs(Thread):
    '''
    Obs class: read text from queue and send it to OBS
    '''
    def __init__(self, read_queue, **kwargs):
        super().__init__(name="OBS_Thrd")
        
        self.credentials = {"host": kwargs.get("OBS", {}).get("host"),
                            "port": kwargs.get("OBS", {}).get("port"),
                            "password": kwargs.get("OBS", {}).get("password")}

        self.subtitle_gdi_text = kwargs.get("OBS", {}).get("subtitle_gdi_text")
        self.disclaimer_gdi_text = kwargs.get("OBS", {}).get("disclaimer_gdi_text")
        self.disclaimer_text = kwargs.get("OBS", {}).get("disclaimer_text")
        self.disclamer_enable = False

        self.read_q = read_queue
        self.stop_process = Event()
        self.ws_obs = None
        self.enable_text = kwargs.get("obs_enable")
        #self.projector = None

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

