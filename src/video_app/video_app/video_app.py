'''
video_app module
creates a dialog from where can be selected the display where video will play in full screen
and the display where the video will resume after stopping the video
'''

import tkinter as tk
from tkinter import ttk
from ch_utils import ch_utils as ut             # pylint: disable=import-error
from video_app.video_proj import VideoProjection

class VideoDialog:
    '''Video dialog class'''

    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Video Monitor Projection")
        self.parent.geometry("400x200")
        self.parent.minsize(width=400, height=200)
        self.parent.maxsize(width=400, height=200)

        self.gui_frame = tk.Frame(parent)
        self.gui_frame.pack(expand=True, anchor=tk.NW)
        self.gui_frame.config(width=400)

        col = 0
        tk.Label(self.gui_frame,
                 text="Start on Display",
                 justify=tk.LEFT).grid(column=col,
                                       row=0,
                                       padx=10,
                                       pady=20)
        tk.Label(self.gui_frame,
                 text="Stop on Display",
                 justify=tk.LEFT).grid(column=col,
                                       row=1,
                                       padx=10,
                                       pady=20)

        data = ut.get_config_info()
        if not data:
            raise Exception("Cannot find the configuration file!")

        for item in data:
            if item.get("application") == "video_projection":
                data = item
                break

        self.displays = data.get("displays")

        col += 1
        self.combo_start = ttk.Combobox(self.gui_frame, values=self.displays)
        self.combo_start.current(0)
        self.combo_start.grid(column=col, row=0, padx=10)

        self.combo_stop = ttk.Combobox(self.gui_frame, values=self.displays)
        self.combo_stop.current(1)
        self.combo_stop.grid(column=col, row=1, padx=10)

        col += 1
        self.start_button = tk.Button(self.gui_frame, text="Start", command=self.start_action)
        self.start_button.grid(column=col, row=0, padx=10)

        self.stop_button = tk.Button(self.gui_frame, text="Stop", command=self.stop_action)
        self.stop_button.grid(column=col, row=1, padx=10)
        self.video_prj = VideoProjection(data.get("app_list", []))

        self.parent.eval("tk::PlaceWindow . center")

    def start_action(self):
        '''start button was pressed'''
        print("Start video!")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        monitor = self.combo_start.current()
        if not self.video_prj.screen_optimizer(self.displays[monitor], fullscreen=True):
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)

    def stop_action(self):
        '''stop button was pressed'''
        print("Stop video!")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        monitor = self.combo_stop.current()
        if not self.video_prj.screen_optimizer(self.displays[monitor]):
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)


root = tk.Tk()
ui = VideoDialog(root)
root.mainloop()
