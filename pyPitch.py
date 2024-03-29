import tkinter as tk
import ttkbootstrap as ttk
from pydub import AudioSegment
from pydub.playback import play
from tkinter import filedialog
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os

window = ttk.Window(themename="darkly")
window.title("pyPitch")
window.geometry('400x450')
window.maxsize(400, 450)
window.minsize(400, 450)

audio = None

class WaveformPlotter:
    def __init__(self, master):
        self.master = master
        self.audio = None
        self.fig = Figure(figsize=(10, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()

        self.canvas_widget.bind("<Button-1>", self.canvas_clicked)
        
    def draw_waveform(self):

        if self.audio is None:
            return
        
        if self.canvas_widget is not None:
            self.canvas_widget.destroy()
        
        self.ax.clear()
        samples = np.array(self.audio.get_array_of_samples())

        duration = len(self.audio) / 1000 
        time = np.linspace(0, duration, num=len(samples))

        self.fig = Figure(figsize=(10, 4))
        self.fig.patch.set_facecolor('#222222')
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(time, samples)
        self.ax.axis('off')
        self.ax.margins(x=0, y=0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=window)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        self.canvas_widget.bind("<Button-1>", self.canvas_clicked)

    def canvas_clicked(self, event):
        if self.audio:
            play(self.audio)

def choose_file(plotter):
    global audio

    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    
    if not file_path.endswith('.wav') and not file_path.endswith('.mp3') and not file_path.endswith('.flac') and not file_path.endswith('.ogg'):
        error_msg.set("Please select a valid audio file!")
        return
    
    audio = AudioSegment.from_file(file_path)

    plotter.audio = audio
    plotter.draw_waveform()

    duration_var.set(round(audio.duration_seconds, 2))

    play_audio_button['state'] = tk.NORMAL
    download_button['state'] = tk.NORMAL
    shift_button['state'] = tk.NORMAL
    f1['state'] = tk.NORMAL
    f2['state'] = tk.NORMAL
    f3['state'] = tk.NORMAL
    f4['state'] = tk.NORMAL


def play_audio():
    if audio:
        play(audio)

def change_pitch():
    global audio

    amt = shift_amt_var.get()

    if not amt.lstrip('-').isdigit():
        error_msg.set("Please enter a valid number!")
        return
    else:
        error_msg.set("")
        pitch_factor = 2 ** (int(amt) / 12)

        audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * pitch_factor)})

        plotter.audio = audio

        duration_var.set(round(audio.duration_seconds, 2))

def download():
    frmt = ''

    directory_path = filedialog.askdirectory()

    if not directory_path:
        return
    
    if format_var.get() == 0:
        frmt = "wav"
    elif format_var.get() == 1:
        frmt = "mp3"
    elif format_var.get() == 2:
        frmt = "flac"
    elif format_var.get() == 3:
        frmt = "ogg"
    
    audio.export(f"{directory_path}/shifted_audio.{frmt}", format=frmt)

def on_slider_move(event):
    shift_amt_var.set(round(slider.get()))

def open_folder():
    
    folder = filedialog.askdirectory()
    if not folder:
        return
    
    save_path = filedialog.askdirectory()
    if not save_path:
        return
    
    if folder:
        for filename in os.scandir(folder):
            if filename.is_file():
                if filename.path.endswith('.wav') or filename.path.endswith('.mp3') or filename.path.endswith('.flac') or filename.path.endswith('.ogg'):
                    audio = AudioSegment.from_file(filename.path)

                    pitch_factor = 2 ** (int(shift_amt_var1.get()) / 12)

                    audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * pitch_factor)})

                    frmt = ''

                    if format_var1.get() == 0:
                        frmt = "wav"
                    elif format_var1.get() == 1:
                        frmt = "mp3"
                    elif format_var1.get() == 2:
                        frmt = "flac"
                    elif format_var1.get() == 3:
                        frmt = "ogg"

                    audio.export(os.path.join(save_path, f"{os.path.basename(filename.path)[:-4]}_shifted_audio.{frmt}"), format=frmt)
    else:
        error_msg.set("Please select a valid folder!")

        
def open_folder_box():
    top = tk.Toplevel(window)
    top.title("Open Folder")
    top.geometry('300x220')
    top.maxsize(300, 220)
    top.minsize(300, 220)
    options_label = ttk.Label(top, text="File Options:", font='Calibri 12', foreground='lightblue')
    options_label.pack(pady=5)

    shift_label = ttk.Label(top, text="Enter pitch shift amount (in semitones):", font="Calibri 10")
    shift_label.pack(pady=5)

    shift_amt = ttk.Entry(top, text='0', width=5, textvariable=shift_amt_var1)
    shift_amt.pack(pady=5)

    format_label = ttk.Label(top, text="Select format:", font='Calibri 10')
    format_label.pack(pady=5)
    
    radio_frame2 = ttk.Frame(top)

    f11 = ttk.Radiobutton(radio_frame2, text="wav", variable=format_var1, value=0)
    f11.pack(side='left', padx=5, pady=5)
    f21 = ttk.Radiobutton(radio_frame2, text="mp3", variable=format_var1, value=1)
    f21.pack(side='left', padx=5, pady=5)
    f31 = ttk.Radiobutton(radio_frame2, text="flac", variable=format_var1, value=2)
    f31.pack(side='left', padx=5, pady=5)
    f41 = ttk.Radiobutton(radio_frame2, text="ogg", variable=format_var1, value=3)
    f41.pack(side='left', padx=5, pady=5)

    radio_frame2.pack()

    open_button = ttk.Button(top, text="Open Folder", command=lambda: (top.destroy(), open_folder()))

    open_button.pack(pady=5)
    top.mainloop()


shift_amt_var = tk.StringVar()
shift_amt_var1 = tk.StringVar()
format_var = tk.IntVar()
format_var1 = tk.IntVar()
error_msg = tk.StringVar()
duration_var = tk.StringVar()

plotter = WaveformPlotter(window)

title = ttk.Label(window, text="Pitch Shifter", font = 'Calibri 24 bold', foreground='lightblue')
title.pack(pady=5)

frame1 = ttk.Frame(window)

choose_file_button = ttk.Button(frame1, text="Choose File", command=lambda: choose_file(plotter))
choose_file_button.pack(side='left', padx=5, pady=5)

open_folder_button = ttk.Button(frame1, text='Choose Folder', command=open_folder_box)
open_folder_button.pack(side='left', pady=5)

play_audio_button = ttk.Button(frame1, text="Play Audio", command=play_audio)
play_audio_button.pack(side='right', pady=5, padx=5)
play_audio_button['state'] = tk.DISABLED

frame1.pack()

shift_label = ttk.Label(window, text="Enter pitch shift amount (in semitones):", font="Calibri 10", foreground='lightblue')
shift_label.pack(pady=5)

slider = ttk.Scale(window, from_=-12, to=12, orient='horizontal', length=300)
slider.pack(pady=5)
slider.bind("<Motion>", on_slider_move)

frame2 = ttk.Frame(window)

shift_amt = ttk.Entry(frame2, text='0', width=5, textvariable=shift_amt_var)
shift_amt.pack(side='left', padx=5, pady=5)

shift_button = ttk.Button(frame2, text="Shift Pitch", command=change_pitch)
shift_button.pack(side='right', padx=5, pady=5)
shift_button['state'] = tk.DISABLED

frame2.pack()

download_button = ttk.Button(window, text="Download Audio", command=download)
download_button.pack(pady=5)
download_button['state'] = tk.DISABLED

radio_frame = ttk.Frame(window)

f1 = ttk.Radiobutton(radio_frame, text="wav", variable=format_var, value=0)
f1.pack(side='left', padx=5, pady=5)
f2 = ttk.Radiobutton(radio_frame, text="mp3", variable=format_var, value=1)
f2.pack(side='left', padx=5, pady=5)
f3 = ttk.Radiobutton(radio_frame, text="flac", variable=format_var, value=2)
f3.pack(side='left', padx=5, pady=5)
f4 = ttk.Radiobutton(radio_frame, text="ogg", variable=format_var, value=3)
f4.pack(side='left', padx=5, pady=5)

f1['state'] = tk.DISABLED
f2['state'] = tk.DISABLED
f3['state'] = tk.DISABLED
f4['state'] = tk.DISABLED

radio_frame.pack()

dur_frame = ttk.Frame(window)

duration_label = ttk.Label(dur_frame, text="Duration: ", font="Calibri 10")
duration_label.pack(side='left', padx=5, pady=5)

duration_value = ttk.Label(dur_frame, text="", font="Calibri 10", textvariable=duration_var, foreground='lightblue')
duration_value.pack(side='right', padx=5, pady=5)

dur_frame.pack()

error_msg_label = ttk.Label(window, textvariable=error_msg, font='Calibri 8', foreground='red')
error_msg_label.pack(pady=2)

window.mainloop()