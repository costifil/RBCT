'''
translate module
'''
import threading
import tkinter as tk
from tkinter import ttk
import time
import logging
from ch_logger.logger_config import setup_logger    # pylint: disable=import-error
from translate_app.producer import Producer         # pylint: disable=import-error
from translate_app.consumer import Consumer         # pylint: disable=import-error
from translate_app.string_queue import StringQueue  # pylint: disable=import-error
from ch_utils import ch_utils as util               # pylint: disable=import-error


class Translate:
    '''Translate dialog class'''
    def __init__(self, breez_conn, obs_conn, **kwargs):
        self.breeze = breez_conn
        self.obs = obs_conn
        self.kwargs = kwargs
        self.strque = StringQueue()
        self.producer = None
        self.consumer = None

        if self.breeze:
            self.producer = Producer(self.strque, **self.kwargs)
        if self.obs:
            self.consumer = Consumer(self.strque, **self.kwargs)

    def start(self):
        '''initiate starting the session'''
        logging.info("\n\t============= Start new session =============")
        logging.info("Breeze is %s!", ("enabled" if self.breeze else "disabled"))
        logging.info("OBS is %s!", ("enabled" if self.obs else "disabled"))
        if self.producer:
            logging.info("Language set to: %s",
                         self.kwargs.get("BreezeTranslate", {}).get("language"))
            self.producer.start()
        if self.consumer:
            self.consumer.start()

    def stop(self):
        '''initiate stopping the session'''
        logging.info("Stop initiated by the user!")
        print("Stop initiated by the user!")
        if self.producer:
            self.producer.stop()
            self.producer = None

        if self.consumer:
            self.consumer.stop()
            self.consumer = None

class TranslateDialog:
    '''Translate dialog class'''
    def __init__(self, parent):
        self.translate = None

        self.data = util.get_config_info()
        for item in self.data:
            if item.get("application") == "translate_subtitle_OBS":
                self.data = item
                break

        json_lang = self.data.get("BreezeTranslate", {}).get("language", "en")
        lang_dict = self.data.get("languages", {})
        lang_key = next((k for k, v in lang_dict.items() if v == json_lang), "English")

        self.language_list = list(lang_dict.keys())

        self.parent = parent
        self.parent.title("Subtitle Translate")
        self.parent.geometry("340x150")
        self.parent.minsize(width=340, height=150)
        self.parent.maxsize(width=340, height=150)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)


        self.gui_frame = tk.Frame(parent)
        self.gui_frame.pack(expand=True, anchor=tk.NW)
        self.gui_frame.config(width=340)

        col = row = 0
        self.check_breeze = tk.BooleanVar(value=True)
        self.breeze_ck = tk.Checkbutton(self.gui_frame,
                                        text="Breeze connection",
                                        variable=self.check_breeze)
        self.breeze_ck.grid(column=col, row=row, padx=20, sticky="w")

        col += 1
        self.check_obs = tk.BooleanVar(value=True)
        self.obs_ck = tk.Checkbutton(self.gui_frame, text="OBS Connection", variable=self.check_obs)
        self.obs_ck.grid(column=col, row=row, padx=20, sticky="w")

        col = 0
        row += 1
        tk.Label(self.gui_frame,
                 text="Language",
                 justify=tk.LEFT).grid(column=col,
                                       row=row,
                                       padx=10,
                                       pady=20)
        col += 1
        self.combo_lang = ttk.Combobox(self.gui_frame, values=self.language_list)
        self.combo_lang.set(lang_key)
        self.combo_lang.grid(column=col, row=row, padx=10, pady=20, sticky="w")

        col = 0
        row += 1
        self.start_button = tk.Button(self.gui_frame,
                                      text="Start",
                                      width=15,
                                      command=self.start_action)
        self.start_button.grid(column=col, row=row, padx=10, pady=20)#, sticky="e")
        self.start_button.config(state=tk.NORMAL)

        col += 1
        self.stop_button = tk.Button(self.gui_frame,
                                     text="Stop",
                                     width=15,
                                     command=self.stop_action)
        self.stop_button.grid(column=col, row=row, padx=10, pady=20)#, sticky="w")
        self.stop_button.config(state=tk.DISABLED)

        self.parent.eval("tk::PlaceWindow . center")

    def set_language(self):
        '''Override the languge from json with the selection from GUI'''
        try:
            if self.data:
                bt = self.data.get("BreezeTranslate")
                ln = self.data.get("languages")
                if bt:
                    lang = self.language_list[self.combo_lang.current()]
                    bt['language'] = ln.get(lang)
                    return

        except Exception as ex:
            logging.error("Fail to set the language:\n%s", ex)

        bt['language'] = "en"

    def start_action(self):
        '''start button was pressed'''
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.set_language()
        self.translate = Translate(self.check_breeze.get(), self.check_obs.get(), **self.data)
        self.translate.start()

    def stop_action(self):
        '''stop button was pressed'''
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.translate:
            self.translate.stop()

    def on_close(self):
        '''on close event in dialog'''
        logging.info("Close Translate application")
        if self.translate:
            self.translate.stop()
            time.sleep(0.5)
        self.parent.destroy()


def main():
    '''main function'''
    threading.current_thread().name = "TranslateThread"
    setup_logger(file_hnd=logging.DEBUG,
                 console_hnd=logging.ERROR) # logging initialized ONCE

    root = tk.Tk()
    TranslateDialog(root)
    root.mainloop()


if __name__ == "__main__":
    main()
