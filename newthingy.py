import numpy as np
from PIL import Image
from scipy.io.wavfile import write

# Load and prepare image (flip vertically)
img = Image.open('qr.png').convert('L').resize((512, 512))
data = np.flipud(np.array(img)) / 255.0  # normalize brightness and flip vertically

sr = 44100
n_freqs, n_time = data.shape

# Audio length scales with image width: 512 pixels → about 0.5 s audio
# Make time vector in seconds (0..duration)
audio_length = sr * n_time // 64
duration = audio_length / sr
t = np.linspace(0.0, duration, audio_length)

frequencies = np.linspace(300, 8000, n_freqs)
audio = np.zeros_like(t)

rng = np.random.default_rng(0)  # for reproducibility
for x in range(n_time):
    # compute per-column time offset in seconds so columns map across the duration
    col_offset = (x / float(n_time)) * duration
    for y in range(n_freqs):
        amp = data[y, x]
        if amp > 0.05:
            freq = frequencies[y]
            phase = rng.random() * 2 * np.pi
            # shift the time axis for this column by col_offset
            audio += amp * np.sin(2 * np.pi * freq * (t - col_offset) + phase)

# Normalize audio safely (avoid division by zero)
max_abs = np.max(np.abs(audio))
if max_abs > 0:
    audio = audio / max_abs

# Save as wav file for playback and analysis
write('image_song.wav', sr, (audio * 32767).astype(np.int16))

# Visualization (run after saving)
import librosa, librosa.display
import matplotlib.pyplot as plt

y, _ = librosa.load('image_song.wav', sr=sr)
X = librosa.stft(y)
Xdb = librosa.amplitude_to_db(abs(X))
plt.figure(figsize=(10, 6))
librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='hz')
plt.colorbar()
plt.show()
