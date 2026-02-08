'''dialog module'''

import tkinter as tk
from tkinter import ttk
import threading
import logging
import time
from ch_logger.logger_config import setup_logger        # pylint: disable=import-error
from translate_app.translate import Translate           # pylint: disable=import-error
from translate_app.producer_text import ProducerText    # pylint: disable=import-error
from translate_app.producer import Producer             # pylint: disable=import-error
from translate_app.projector import ProjectorDialog     # pylint: disable=import-error
from translate_app.consumer import Consumer             # pylint: disable=import-error
from ch_utils import ch_utils as util                   # pylint: disable=import-error


class TranslateDialog(tk.Toplevel):
    '''Translate dialog class'''
    def __init__(self, parent):
        super().__init__(parent)
        self.root = parent
        self.translate = None
        self.projector_dialog = None

        self.data = util.get_config_info()
        for item in self.data:
            if item.get("application") == "translate_subtitle_app":
                self.data = item
                break

        json_language = self.data.get("BreezeTranslate", {}).get("language", "en")
        language_dict = self.data.get("languages", {})
        lang_key = next((k for k, v in language_dict.items() if v == json_language), "English")

        self.language_list = list(language_dict.keys())

        # self.parent = parent
        # self.parent.title("Subtitle Translate")
        # self.parent.geometry("340x200")
        # self.parent.minsize(width=340, height=200)
        # self.parent.maxsize(width=340, height=200)
        # self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

        self.title("Translate App")
        self.geometry("340x200")
        self.minsize(width=340, height=180)
        self.maxsize(width=340, height=180)
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
        self.obs_ck = tk.Checkbutton(self.gui_frame,
                                     text="OBS Connection",
                                     variable=self.check_obs,
                                     command=self.on_obs_check)
        self.obs_ck.grid(column=col, row=row, padx=20, sticky="w")

        col = 1
        row += 1
        self.check_projector = tk.BooleanVar(value=False)
        self.projection_ck = tk.Checkbutton(self.gui_frame,
                                            text="Projector connection",
                                            variable=self.check_projector,
                                            command=self.on_projection_check)
        self.projection_ck.grid(column=col, row=row, padx=20, sticky="w")
        
        # self.projector_button = tk.Button(self.gui_frame,
                                          # text="Projector Dialog",
                                          # width=15,
                                          # command=self.open_projector_dialog)
        # self.projector_button.grid(column=col, row=row, padx=10, pady=20)
        # self.projector_button.config(state=tk.NORMAL)

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
        if self.projector_dialog is None or not self.projector_dialog.winfo_exists():
            self.projector_dialog = ProjectorDialog(self)
        else:
            self.projector_dialog.lift()

    def start_action(self):
        '''start button was pressed'''
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.set_language()
        self.translate = Translate(self.check_breeze.get(),
                                   self.check_obs.get(),
                                   self.check_projector.get(),
                                   **self.data)
        self.translate.start(self.projector_dialog)

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

    def on_projection_check(self):
        '''enable/disable projector check'''
        print("On projection_check")
        if self.check_projector.get():
            print("On projection_check:", self.projector_dialog)
            if self.projector_dialog is None or not self.projector_dialog.winfo_exists():
                self.projector_dialog = ProjectorDialog(self)
            else:
                self.projector_dialog.lift()
                self.projector_dialog.deiconify()
        else:
            print("On projection_check hide:", self.projector_dialog)
            # hide projector dialog
            if self.projector_dialog:
                self.projector_dialog.withdraw()
                #self.projector_dialog.on_close()
                #self.projector_dialog = None

    def on_close(self):
        '''on close event in dialog'''
        logging.info("Close Translate application")
        if self.translate:
            self.translate.stop()
            time.sleep(0.5)

        self.destroy()
        self.root.destroy()

def main():
    '''main function'''
    threading.current_thread().name = "TranslateThread"
    setup_logger(file_hnd=logging.DEBUG,
                 console_hnd=logging.ERROR) # logging initialized ONCE

    root = tk.Tk()
    root.withdraw()

    #if os.path.exists("CC.ico"):
    #    root.iconbitmap("CC.ico")
    TranslateDialog(root)
    root.mainloop()


if __name__ == "__main__":
    main()
