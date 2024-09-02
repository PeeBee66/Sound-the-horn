import tkinter as tk
from tkinter import messagebox
import time
import threading
import pyaudio
import wave
import os

# Define sound files
SOUND_FILES = ["sounds1.ogg", "sounds2.ogg", "sounds3.ogg"]

# Check if the sound file exists
def check_sound_files():
    for sound_file in SOUND_FILES:
        if not os.path.exists(sound_file):
            messagebox.showerror("Error", f"Sound file {sound_file} not found")
            return False
    return True

# Dummy function for sound detection
def detect_sound():
    # This function should be replaced with actual sound detection logic
    time.sleep(1)
    return SOUND_FILES[0]

class SoundHornApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sound the Horn")
        self.root.geometry("300x200")
        self.root.attributes('-topmost', True)

        self.cast_key = tk.StringVar(value="f")
        self.catch_key = tk.StringVar(value="g")
        self.running = False

        self.create_widgets()

    def create_widgets(self):
        settings_frame = tk.LabelFrame(self.root, text="Settings")
        settings_frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(settings_frame, text="Cast Key:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(settings_frame, textvariable=self.cast_key).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(settings_frame, text="Catch Key:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(settings_frame, textvariable=self.catch_key).grid(row=1, column=1, padx=5, pady=5)

        self.start_button = tk.Button(settings_frame, text="Start", command=self.start)
        self.start_button.grid(row=2, column=0, padx=5, pady=5)

        self.stop_button = tk.Button(settings_frame, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, padx=5, pady=5)

        self.status_label = tk.Label(self.root, text="Status: Idle")
        self.status_label.pack(pady=10)

    def start(self):
        if not check_sound_files():
            return
        
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Starting in 5 seconds...")
        self.root.after(5000, self.run)

    def stop(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped")

    def run(self):
        if not self.running:
            return

        self.status_label.config(text="Status: Casting...")
        self.simulate_key_press(self.cast_key.get())
        self.status_label.config(text="Status: Listening...")

        sound_detected = detect_sound()
        if sound_detected:
            self.status_label.config(text=f"Status: Match detected ({sound_detected})")
            wait_time = 0.5 + (1.5 * time.time() % 1)  # Random wait between 0.5 and 2 seconds
            self.root.after(int(wait_time * 1000), self.catch)

    def catch(self):
        if not self.running:
            return

        self.status_label.config(text="Status: Catching...")
        self.simulate_key_press(self.catch_key.get())
        self.root.after(1000, self.run)  # Repeat the process after 1 second

    def simulate_key_press(self, key):
        # Simulate key press (this is a placeholder)
        print(f"Simulating key press: {key}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundHornApp(root)
    root.mainloop()
