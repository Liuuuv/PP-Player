from pydub import AudioSegment
import numpy as np


def generate_waveform_preview(self, filepath, resolution=5000):
        try:
            audio = AudioSegment.from_file(filepath)
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)

            samples = samples[::len(samples)//resolution or 1]
            self.waveform_data = samples / max(abs(samples).max(), 1)  # Normalisé
        except Exception as e:
            self.status_bar.config(text=f"Erreur waveform preview: {e}")
            self.waveform_data = None