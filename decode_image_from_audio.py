"""
Decode an image encoded into audio by `newthingy.py`.

This script expects `image_song.wav` in the same folder. It computes an STFT,
maps frequency bins linearly to rows (300..8000 Hz → top..bottom), maps
STFT frames to image columns, and writes a recovered grayscale PNG.

Usage: python decode_image_from_audio.py

Requirements: numpy, scipy, librosa, Pillow
"""
import numpy as np
from scipy.io import wavfile
from PIL import Image
import librosa
import librosa.display


def decode(wav_path='image_song.wav', out_image='recovered.png', n_rows=512, fmin=300, fmax=8000, sr_target=None):
    # Load audio (use librosa to preserve mono and type)
    y, sr = librosa.load(wav_path, sr=sr_target, mono=True)

    # STFT params: choose hop and window so number of time frames ~ columns
    # We'll compute an STFT and then resize columns to n_cols later.
    n_fft = 4096
    hop_length = 512

    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop_length, n_fft=n_fft)

    # Determine frequency bin indices corresponding to fmin..fmax
    freq_mask = (freqs >= fmin) & (freqs <= fmax)
    freqs_in_band = freqs[freq_mask]
    S_band = S[freq_mask, :]

    # Map frequency bins to image rows (n_rows). If bins != n_rows, resample along freq axis
    if S_band.shape[0] != n_rows:
        # linear interpolation along frequency axis
        orig_idx = np.linspace(0, S_band.shape[0] - 1, S_band.shape[0])
        target_idx = np.linspace(0, S_band.shape[0] - 1, n_rows)
        S_resampled = np.zeros((n_rows, S_band.shape[1]), dtype=float)
        for col in range(S_band.shape[1]):
            S_resampled[:, col] = np.interp(target_idx, orig_idx, S_band[:, col])
    else:
        S_resampled = S_band

    # Map STFT frames to image columns. The original script used n_time = image width.
    # We'll estimate n_cols as the original n_time by scaling frames to columns.
    n_cols = 512
    if S_resampled.shape[1] != n_cols:
        # resample along time axis
        orig_idx = np.linspace(0, S_resampled.shape[1] - 1, S_resampled.shape[1])
        target_idx = np.linspace(0, S_resampled.shape[1] - 1, n_cols)
        img = np.zeros((n_rows, n_cols), dtype=float)
        for row in range(n_rows):
            img[row, :] = np.interp(target_idx, orig_idx, S_resampled[row, :])
    else:
        img = S_resampled

    # Normalize to 0..255 and flip vertically (encoder flipped vertically)
    img = img - img.min()
    if img.max() > 0:
        img = img / img.max()
    img = np.flipud(img)
    img_u8 = (img * 255).astype(np.uint8)
    im = Image.fromarray(img_u8, mode='L')
    im.save(out_image)
    print(f"Saved recovered image to {out_image}")


if __name__ == '__main__':
    decode()
