"""
Demodulation-based decoder for `image_song.wav` produced by `newthingy.py`.

This script performs coherent demodulation (matched-filter) per target frequency and
per-column time window to recover the image more clearly than a plain spectrogram.

Usage: python demod_decode.py

Requirements: numpy, scipy, Pillow
"""
import numpy as np
from scipy.io import wavfile
from PIL import Image


def demod_decode(wav_path='image_song.wav', out_image='recovered_demod.png', n_rows=512, n_cols=512, fmin=300.0, fmax=8000.0):
    # Read wav file (scipy gives fs and int16 signal)
    sr, data = wavfile.read(wav_path)
    # Convert to float, mono
    if data.ndim > 1:
        data = data.mean(axis=1)
    y = data.astype(np.float64)
    # normalize
    if np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y))

    total_samples = y.shape[0]
    duration = total_samples / float(sr)

    # Frequencies for each row
    freqs = np.linspace(fmin, fmax, n_rows)

    # Determine per-column sample ranges
    # Encoder used n_time = 512 columns across full duration
    col_duration = duration / float(n_cols)
    col_samples = int(round(col_duration * sr))

    # Precompute reference signals for each freq for one column duration
    t_col = np.linspace(0.0, col_duration, col_samples, endpoint=False)
    refs_sin = np.sin(2.0 * np.pi * freqs[:, None] * t_col)
    refs_cos = np.cos(2.0 * np.pi * freqs[:, None] * t_col)

    # Allocate image
    img = np.zeros((n_rows, n_cols), dtype=float)

    # For each column, extract the chunk and compute complex demod (dot product)
    for col in range(n_cols):
        start = col * col_samples
        end = start + col_samples
        if start >= total_samples:
            break
        chunk = y[start:end]
        # If last chunk is shorter, pad with zeros
        if chunk.shape[0] < col_samples:
            chunk = np.pad(chunk, (0, col_samples - chunk.shape[0]))
        # Compute in-band complex amplitude via dot with sin/cos
        # Multiply chunk (1d) with refs and sum along time axis
        # result: arrays of length n_rows
        sin_proj = refs_sin.dot(chunk)
        cos_proj = refs_cos.dot(chunk)
        amp = np.sqrt(sin_proj**2 + cos_proj**2)
        img[:, col] = amp

    # Normalize, flip vertically and save
    img -= img.min()
    if img.max() > 0:
        img = img / img.max()
    img = np.flipud(img)
    img_u8 = (img * 255).astype(np.uint8)
    Image.fromarray(img_u8, mode='L').save(out_image)
    print(f"Saved demodulated image to {out_image}")


if __name__ == '__main__':
    demod_decode()
