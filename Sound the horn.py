import tkinter as tk
from tkinter import ttk, messagebox
import pyaudio
import numpy as np
import threading
import time

class SoundTheHornGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sound the Horn")
        self.master.geometry("500x400")
        self.master.resizable(False, False)
        
        self.is_running = False
        
        try:
            self.p = pyaudio.PyAudio()
        except Exception as e:
            self.show_error("PyAudio Initialization Error", f"Failed to initialize PyAudio: {str(e)}")
            self.p = None
        
        self.stream = None
        self.audio_data = np.array([])
        self.RATE = 44100
        self.CHUNK = 1024
        
        self.create_widgets()
        self.start_audio_stream()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Sound the Horn", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Cast Button
        ttk.Label(main_frame, text="Cast Button").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cast_button_var = tk.StringVar(value='f')
        self.cast_button_entry = ttk.Entry(main_frame, textvariable=self.cast_button_var, width=5)
        self.cast_button_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Pull up cast Button
        ttk.Label(main_frame, text="Pull up cast").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.pull_up_button_var = tk.StringVar(value='g')
        self.pull_up_button_entry = ttk.Entry(main_frame, textvariable=self.pull_up_button_var, width=5)
        self.pull_up_button_entry.grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # Audio line select
        ttk.Label(main_frame, text="Select audio cable").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.audio_output = ttk.Combobox(main_frame, state="readonly", width=40)
        self.audio_output.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.populate_audio_devices()
        
        # Log area
        ttk.Label(main_frame, text="Log").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.log_text = tk.Text(main_frame, height=10, width=60)
        self.log_text.grid(row=4, column=0, columnspan=4, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Buttons
        self.start_button = ttk.Button(main_frame, text="Start", command=self.start_analysis)
        self.start_button.grid(row=5, column=0, pady=10)
        
        self.load_button = ttk.Button(main_frame, text="Load", command=self.load_sound_templates)
        self.load_button.grid(row=5, column=1, pady=10)
        
        self.db_label = ttk.Label(main_frame, text="DB: 0")
        self.db_label.grid(row=5, column=2, pady=10)
        
        self.stop_button = ttk.Button(main_frame, text="Stop", command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.grid(row=5, column=3, pady=10)
        
    def populate_audio_devices(self):
        if self.p is None:
            self.log("Audio system not available. Cannot populate devices.")
            return
        
        devices = []
        try:
            for i in range(self.p.get_device_count()):
                dev = self.p.get_device_info_by_index(i)
                if dev['maxInputChannels'] > 0:
                    devices.append((i, dev['name']))
            self.audio_output['values'] = [dev[1] for dev in devices]
            if devices:
                self.audio_output.set(devices[0][1])
            else:
                self.log("No audio input devices found.")
        except Exception as e:
            self.log(f"Error populating audio devices: {str(e)}")
    
    def load_sound_templates(self):
        self.log("Sound template loading not implemented yet.")
        
    def start_analysis(self):
        self.log("Sound analysis not implemented yet.")
        
    def stop_analysis(self):
        self.log("Sound analysis stop not implemented yet.")
        
    def start_audio_stream(self):
        if self.p is None:
            self.log("Audio system not available. Cannot start audio stream.")
            return
        
        try:
            device_index = self.audio_output.current()
            self.stream = self.p.open(format=pyaudio.paFloat32,
                                      channels=1,
                                      rate=self.RATE,
                                      input=True,
                                      input_device_index=device_index,
                                      frames_per_buffer=self.CHUNK,
                                      stream_callback=self.audio_callback)
            self.stream.start_stream()
            self.log("Audio stream started")
            threading.Thread(target=self.update_db, daemon=True).start()
        except Exception as e:
            self.log(f"Error starting audio stream: {str(e)}")
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        if status:
            self.log(f"Audio stream status: {status}")
        self.audio_data = np.frombuffer(in_data, dtype=np.float32)
        return (in_data, pyaudio.paContinue)
    
    def update_db(self):
        while True:
            if len(self.audio_data) > 0:
                rms = np.sqrt(np.mean(self.audio_data**2))
                db = 20 * np.log10(max(rms, 10**-10))
                db = max(0, min(db, 100))  # Clamp between 0 and 100
                self.master.after(0, lambda d=db: self.db_label.config(text=f"DB: {d:.1f}"))
            time.sleep(0.1)
    
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def __del__(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundTheHornGUI(root)
    root.mainloop()