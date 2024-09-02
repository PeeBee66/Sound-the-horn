import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyaudio
import numpy as np
import threading
import time
import wave
import struct

class TestLineDB:
    def __init__(self, master):
        self.master = master
        master.title("Test Line DB")
        master.geometry("400x250")

        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False
        self.is_recording = False
        self.recorded_frames = []

        self.create_widgets()
        self.input_devices = self.get_input_devices()
        self.populate_device_menu()

    def create_widgets(self):
        # Device selection
        ttk.Label(self.master, text="Select Input Device:").pack(pady=5)
        self.device_var = tk.StringVar()
        self.device_menu = ttk.Combobox(self.master, textvariable=self.device_var)
        self.device_menu.pack(pady=5)
        self.device_menu.bind("<<ComboboxSelected>>", self.on_device_select)

        # DB Level display
        self.db_var = tk.StringVar(value="DB Level: 0 dB")
        ttk.Label(self.master, textvariable=self.db_var, font=("Arial", 16)).pack(pady=20)

        # Button frame
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=10)

        # Start/Stop button
        self.toggle_button = ttk.Button(button_frame, text="Start", command=self.toggle_monitoring)
        self.toggle_button.grid(row=0, column=0, padx=5)

        # Record button
        self.record_button = ttk.Button(button_frame, text="Record", command=self.toggle_recording, state=tk.DISABLED)
        self.record_button.grid(row=0, column=1, padx=5)

        # Recording indicator
        self.recording_indicator = ttk.Label(self.master, text="", font=("Arial", 10, "bold"))
        self.recording_indicator.pack(pady=5)

    def get_input_devices(self):
        input_devices = []
        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            if dev_info['maxInputChannels'] > 0:
                input_devices.append((dev_info['index'], dev_info['name']))
        return input_devices

    def populate_device_menu(self):
        device_names = [device[1] for device in self.input_devices]
        self.device_menu['values'] = device_names
        if device_names:
            self.device_menu.set(device_names[0])

    def on_device_select(self, event):
        if self.is_running:
            self.stop_monitoring()
            self.start_monitoring()

    def toggle_monitoring(self):
        if self.is_running:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        selected_device = self.device_var.get()
        device_index = next(device[0] for device in self.input_devices if device[1] == selected_device)

        try:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      input_device_index=device_index,
                                      frames_per_buffer=1024,
                                      stream_callback=self.audio_callback)
            self.stream.start_stream()
            self.is_running = True
            self.toggle_button.config(text="Stop")
            self.record_button.config(state=tk.NORMAL)
            threading.Thread(target=self.update_db, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start audio stream: {str(e)}")

    def stop_monitoring(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.is_running = False
        self.toggle_button.config(text="Start")
        self.record_button.config(state=tk.DISABLED)
        self.db_var.set("DB Level: 0 dB")
        if self.is_recording:
            self.stop_recording()

    def audio_callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Calculate dB level
        rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
        db = 20 * np.log10(max(rms, 1e-10))
        self.master.after(0, lambda: self.db_var.set(f"DB Level: {db:.2f} dB"))

        if self.is_recording:
            self.recorded_frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def update_db(self):
        while self.is_running:
            time.sleep(0.1)

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recorded_frames = []
        self.is_recording = True
        self.record_button.config(text="Stop Recording")
        self.recording_indicator.config(text="Recording...", foreground="red")

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Record")
        self.recording_indicator.config(text="")
        self.save_recording()

    def save_recording(self):
        if not self.recorded_frames:
            messagebox.showinfo("Info", "No audio recorded.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".wav",
                                                 filetypes=[("Wave files", "*.wav")])
        if file_path:
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.recorded_frames))
            wf.close()
            messagebox.showinfo("Success", f"Recording saved to {file_path}")

    def __del__(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = TestLineDB(root)
    root.mainloop()