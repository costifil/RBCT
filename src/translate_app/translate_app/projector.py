import tkinter as tk

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
        #logging.info("Close Projector Dialog")
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
