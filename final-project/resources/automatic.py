from pyaudio import PyAudio
import numpy as np
import sounddevice as sd
from .projGlobals import *

# Number of samples per FFT. Should be a power of 2.
FFT_LEN = 4096

class AutomaticDetection:

    def __init__(self):
        self.dom_freq = 0.0
        self.notes = list(NOTES_DICT.values())
        self.nearest_note = ""
        self.nearest_pitch = ""
        self.rec_dev_num = None
        self.rec_dev_name = None
        self.buffer = np.array([], dtype=np.float64)
        self.frames_processed = 0

    def selectRecordingDevice(self):
        termClear()
        device_list = dict()
        p = PyAudio()
        info = p.get_host_api_info_by_index(host_api_index=0)
        for i in range(info.get("deviceCount")):
            if p.get_device_info_by_host_api_device_index(0, i).get(
                "maxInputChannels"
            ):
                devInfo = p.get_device_info_by_host_api_device_index(0, i)
                iInfo = devInfo.get("index")
                nInfo = devInfo.get("name")
                device_list[iInfo] = nInfo

        opt = -1
        conf = "n"
        while opt < 1 or opt > len(device_list) or conf != "Y".lower():
            print(
                "Select which device to use for live audio processing "
                "and note comparison: "
            )
            try:
                for d in device_list:
                    print(f"   #{d} - Name: {device_list[d]}")
                opt = int(input("\nPlease enter which device number to use: "))
            except ValueError:
                opt = -1
                termClear()
                print("Invalid option...\n")
                continue
            if opt not in device_list:
                opt = -1
                termClear()
                print("Invalid option...\n")
                continue
            else:
                print(f"Selected device --> {device_list[opt]}.")
                conf = input("Is this correct? Y/N: ").lower()
                if conf != "y":
                    conf = "n"
                    termClear()
                    continue

        self.rec_dev_num = opt
        self.rec_dev_name = device_list[opt]
        return

    def nearest_neighbor(self):
        notes_len = len(self.notes)
        n = int(np.round((self.dom_freq / PITCH_CHECK) * notes_len))
        self.nearest_note = self.notes[n % notes_len]
        self.nearest_pitch = PITCH_CHECK * 2 ** (n / notes_len)
        return

    def callback(self, inputD: np.ndarray, frames, dur, state):
        if any(inputD):
            if len(self.buffer) >= FFT_LEN + frames:
                self.buffer = self.buffer[frames:]
            self.buffer = np.append(self.buffer, inputD.flatten())
            fft_res = np.fft.fft(self.buffer[:FFT_LEN])
            magnitude = np.abs(fft_res)
            freqs = np.fft.fftfreq(fft_res.size, 1 / SAMPLE_RATE)
            positive_mask = freqs > 0
            dom_freq_idx = np.argmax(magnitude[positive_mask])
            self.dom_freq = freqs[positive_mask][dom_freq_idx]
            self.nearest_neighbor()
            if self.frames_processed % int(0.1 * SAMPLE_RATE) == 0:
                termClear()
                expt_freq = float(
                    "{:.3f}".format(NOTES_TO_FREQ_DICT[self.nearest_note])
                )
                freq_diff = float("{:.3f}".format(expt_freq - self.dom_freq))
                if expt_freq > self.dom_freq:
                    freq_diff *= -1
                print(
                    f"Nearest note: {self.nearest_note}\n"
                    f"Expected freq: {expt_freq}\n"
                    f"Actual freq: {self.dom_freq}\n"
                    f"{freqDifference(self.nearest_note, freq_diff)}\n"
                    "CTRL+C to return to main menu!",
                    end="\r",
                )
            self.frames_processed += frames
        else:
            print(
                "Waiting for you to play!\n"
                "If you are, make sure your device is plugged in.\n"
                "CTRL+C to return to main menu!",
                end="\r",
            )
            print()

    def autoStart(self):
        termClear()
        self.selectRecordingDevice()
        try:
            stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                blocksize=64,
                device=self.rec_dev_num,
                channels=1,
                callback=self.callback,
            )
            stream.start()
            sd.wait()
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    ad = AutomaticDetection()
    ad.autoStart()
