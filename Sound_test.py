import pyaudio
import wave
import numpy as np

def list_input_devices():
    p = pyaudio.PyAudio()
    input_devices = []
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info['maxInputChannels'] > 0:  # Only list input devices
            print(f"{len(input_devices)}. {dev_info['name']}")
            input_devices.append(i)
    p.terminate()
    return input_devices

def test_audio_line(device_index):
    p = pyaudio.PyAudio()
    dev_info = p.get_device_info_by_index(device_index)
    print(f"\nTesting device: {dev_info['name']}")

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = min(2, dev_info['maxInputChannels'])  # Use max 2 channels
    RATE = int(dev_info['defaultSampleRate'])
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = f"audio_test_{device_index}.wav"

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK)

        print(f"Recording {RECORD_SECONDS} seconds of audio...")
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Recording finished.")

        stream.stop_stream()
        stream.close()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Audio saved to {WAVE_OUTPUT_FILENAME}")

        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        max_amplitude = np.max(np.abs(audio_data))
        if max_amplitude > 0:
            print(f"Audio detected. Max amplitude: {max_amplitude}")
        else:
            print("No significant audio detected. Check if the device is receiving audio.")

    except Exception as e:
        print(f"Error testing audio line: {str(e)}")

    finally:
        p.terminate()

if __name__ == "__main__":
    print("Available input devices:")
    input_devices = list_input_devices()

    while True:
        try:
            choice = int(input("\nEnter the number of the device you want to test (or -1 to quit): "))
            if choice == -1:
                break
            if 0 <= choice < len(input_devices):
                test_audio_line(input_devices[choice])
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")