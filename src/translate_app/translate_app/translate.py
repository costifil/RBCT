'''
translate module
'''
import os
import threading
import tkinter as tk
from tkinter import ttk
import time
import logging
from ch_logger.logger_config import setup_logger        # pylint: disable=import-error
from translate_app.producer_text import ProducerText    # pylint: disable=import-error
from translate_app.breeze import Breeze                 # pylint: disable=import-error
from translate_app.obs import Obs                       # pylint: disable=import-error
from translate_app.string_queue import StringQueue      # pylint: disable=import-error
from ch_utils import ch_utils as util                   # pylint: disable=import-error


class Translate:
    '''Translate dialog class'''
    def __init__(self, breez_chk, obs_chk, projector_chk, **kwargs):
        self.breez_chk = breez_chk
        self.obs_chk = obs_chk
        self.projector_chk = projector_chk
        self.kwargs = kwargs

        self.producer_obj = None # this is Breeze or ProducerText
        self.obs_obj = None
        self.projector_obj = None

        self.queues = [StringQueue() for _ in range(2)]

        if self.breez_chk:
            self.producer_obj = Breeze(self.queues, **kwargs)
        else:
            # Breeze was disabled - start producer text
            self.producer_obj = ProducerText(self.queues, **kwargs)

        if self.obs_chk:
            self.kwargs['obs_enable'] = self.obs_chk
            self.obs_obj = Obs(self.queues[0], **self.kwargs)

        #if self.projector_chk:
        #    self.projector_obj = Projector(self.queues[1], **self.kwargs)

    def start(self, projector_obj=None):
        '''initiate starting the session'''
        #if proj_obj:
        #    self.proj_dialog = proj_obj

        #logging.info("\n\t============= Start new session =============")
        #logging.info("Breeze is %s!", ("enabled" if self.breeze else "disabled"))
        #logging.info("OBS is %s!", ("enabled" if self.obs else "disabled"))
        if self.producer_obj:
            self.producer_obj.set_projector_obj(projector_obj)
            #logging.info("Language set to: %s",
            #             self.kwargs.get("BreezeTranslate", {}).get("language"))
            self.producer_obj.start()

        if self.obs_obj:
            #self.consumer.init_projector(self.proj_dialog)
            self.obs_obj.start(self.strque, **self.kwargs)

    def stop(self):
        '''initiate stopping the session'''
        logging.info("Stop initiated by the user!")
        print("Stop initiated by the user!")
        if self.producer_obj:
            self.producer_obj.stop()
            self.producer_obj = None

        if self.obs_obj:
            self.obs_obj.stop()
            self.obs_obj = None


class TranslateOld:
    '''Translate dialog class'''
    def __init__(self, breez_conn, obs_conn, projector_conn, **kwargs):
        self.breeze = breez_conn
        self.obs = obs_conn
        self.kwargs = kwargs
        # for 2 consumers I need 2 queues. One for each consumer 
        # and the producer will produce in both queues
        self.strque = StringQueue()
        self.producer = None
        self.consumer = None
        self.proj_dialog = None

        if self.breeze:
            self.producer = Producer(self.strque, **self.kwargs)
        else:
            # start producer text as Breeze was disabled
            self.producer = ProducerText(self.strque, **self.kwargs)

        self.kwargs['obs_enable'] = self.obs
        self.consumer = Consumer(self.strque, **self.kwargs)

    def start(self, proj_obj=None):
        '''initiate starting the session'''
        if proj_obj:
            self.proj_dialog = proj_obj

        logging.info("\n\t============= Start new session =============")
        logging.info("Breeze is %s!", ("enabled" if self.breeze else "disabled"))
        logging.info("OBS is %s!", ("enabled" if self.obs else "disabled"))
        if self.producer:
            logging.info("Language set to: %s",
                         self.kwargs.get("BreezeTranslate", {}).get("language"))
            self.producer.start()

        if self.consumer:
            self.consumer.init_projector(self.proj_dialog)
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


class ProjectorDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Projector")
        self.geometry("640x400")
        #self.geometry(f"800x600+{m.x}+{m.y}") where m is the monitor number

        self.text_box = tk.Text(self, fg="white", bg="black", font=("Arial", 40))
        self.text_box.pack(expand=True, fill="both")

    def on_close(self):
        '''on close event in dialog'''
        logging.info("Close Projector Dialog")
        self.destroy()

    def send_text(self, message):
        print("ProjectorDialog::send_text: ", message)
        if message:
            self.text_box.insert("end", message + "\n")
            self.text_box.see("end")
            self.trim_lines(20)

        lines = int(self.text_box.index("end-1c").split(".")[0])
        print("lines:", lines)

    def trim_lines(self, max_lines):
        lines = int(self.text_box.index("end-1c").split(".")[0])
        while lines > max_lines:
            self.text_box.delete("1.0", "2.0")
            lines -= 1

class TranslateDialog(tk.Toplevel):
    '''Translate dialog class'''
    def __init__(self, parent):
        super().__init__(parent)
        self.root = parent
        self.translate = None
        self.proj_dialog = None

        self.data = util.get_config_info()
        for item in self.data:
            if item.get("application") == "translate_subtitle_OBS":
                self.data = item
                break

        json_lang = self.data.get("BreezeTranslate", {}).get("language", "en")
        lang_dict = self.data.get("languages", {})
        lang_key = next((k for k, v in lang_dict.items() if v == json_lang), "English")

        self.language_list = list(lang_dict.keys())

        # self.parent = parent
        # self.parent.title("Subtitle Translate")
        # self.parent.geometry("340x200")
        # self.parent.minsize(width=340, height=200)
        # self.parent.maxsize(width=340, height=200)
        # self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

        self.title("Subtitle Translate")
        self.geometry("340x200")
        self.minsize(width=340, height=200)
        self.maxsize(width=340, height=200)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        #self.gui_frame = tk.Frame(parent)
        self.gui_frame = tk.Frame(self)
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
        self.obs_ck = tk.Checkbutton(self.gui_frame, text="OBS Connection", variable=self.check_obs, command=self.on_obs_check)
        self.obs_ck.grid(column=col, row=row, padx=20, sticky="w")

        col = 1
        row += 1
        self.projector_button = tk.Button(self.gui_frame,
                                          text="Projector Dialog",
                                          width=15,
                                          command=self.open_projector_dialog)
        self.projector_button.grid(column=col, row=row, padx=10, pady=20)
        self.projector_button.config(state=tk.NORMAL)

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

        #self.parent.eval("tk::PlaceWindow . center")


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

    def open_projector_dialog(self):
        if self.proj_dialog is None or not self.proj_dialog.winfo_exists():
            self.proj_dialog = ProjectorDialog(self)
        else:
            self.proj_dialog.lift()

    def start_action(self):
        '''start button was pressed'''
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.set_language()
        self.translate = Translate(self.check_breeze.get(),
                                   self.check_obs.get(),
                                   **self.data)
        self.translate.start(self.proj_dialog)

    def stop_action(self):
        '''stop button was pressed'''
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.translate:
            self.translate.stop()

    def on_obs_check(self):
        '''enable/disable obs check'''
        val = self.check_obs.get()
        if self.translate and self.translate.consumer:
            self.translate.consumer.enable_subtitle(val)

    def on_close(self):
        '''on close event in dialog'''
        logging.info("Close Translate application")
        if self.translate:
            self.translate.stop()
            time.sleep(0.5)
        #self.parent.destroy()
        self.destroy()
        self.root.destroy()


def main():
    '''main function'''
    threading.current_thread().name = "TranslateThread"
    setup_logger(file_hnd=logging.DEBUG,
                 console_hnd=logging.ERROR) # logging initialized ONCE

    root = tk.Tk()
    root.withdraw()

    if os.path.exists("CC.ico"):
        root.iconbitmap("CC.ico")
    TranslateDialog(root)
    root.mainloop()


if __name__ == "__main__":
    main()
