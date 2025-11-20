#!/usr/bin/env python3
"""Deepgram ASR with Noisereduce - Streaming Telephony Denoising"""
import os
import io
import numpy as np
from scipy.io import wavfile
import noisereduce as nr
from flask import Flask, request, jsonify
from flask_cors import CORS
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

app = Flask(__name__)
CORS(app)

# Config
PORT = int(os.getenv('PORT', 6010))
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
SPEECH_MODEL = os.getenv('SPEECH_RECOGNITION_MODEL', 'nova-2-phonecall')
SPEECH_LANG = os.getenv('SPEECH_RECOGNITION_LANGUAGE', 'en-US')
ENABLE_DENOISING = os.getenv('ENABLE_DENOISING', 'true').lower() == 'true'
NOISE_THRESHOLD = float(os.getenv('NOISE_THRESHOLD', '1.5'))

# Load noise sample
noise_sample = None
if os.path.exists('noise_sample.npy'):
    noise_sample = np.load('noise_sample.npy')
    print(f"✅ Noise sample loaded: {noise_sample.shape}")
else:
    print("⚠️ No noise sample; using non-stationary mode")

deepgram = DeepgramClient(DEEPGRAM_API_KEY)

def denoise_audio(audio_data, sample_rate=8000):
    if not ENABLE_DENOISING:
        return audio_data
    
    try:
        # Normalize & mono
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        data_float = audio_data.astype(np.float32) / 32768.0
        
        # Denoise
        if noise_sample is not None and len(noise_sample) > 0:
            cleaned = nr.reduce_noise(
                y=data_float, sr=sample_rate, y_noise=noise_sample,
                stationary=True, n_std_thresh_stationary=NOISE_THRESHOLD,
                prop_decrease=0.9, n_fft=512, hop_length=128
            )
        else:
            cleaned = nr.reduce_noise(
                y=data_float, sr=sample_rate,
                stationary=False, n_std_thresh_stationary=NOISE_THRESHOLD,
                prop_decrease=0.9, n_fft=512, hop_length=128
            )
        
        return (cleaned * 32767).astype(np.int16)
    except Exception as e:
        print(f"❌ Denoising error: {e}")
        return audio_data

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'denoising': ENABLE_DENOISING, 'model': SPEECH_MODEL})

@app.route('/speech-to-text-stream', methods=['POST'])
def speech_to_text():
    try:
        audio_bytes = request.data
        if not audio_bytes:
            return jsonify({'error': 'No audio'}), 400
        
        # Parse WAV
        audio_io = io.BytesIO(audio_bytes)
        sample_rate, audio_data = wavfile.read(audio_io)
        
        # Denoise
        if ENABLE_DENOISING:
            audio_data = denoise_audio(audio_data, sample_rate)
            print(f"🔇 Denoised audio: {len(audio_data)} samples @ {sample_rate}Hz")
        
        # Re-WAV for Deepgram
        clean_io = io.BytesIO()
        wavfile.write(clean_io, sample_rate, audio_data)
        clean_bytes = clean_io.getvalue()
        
        # Transcribe
        source = FileSource.from_buffer(clean_bytes)
        options = PrerecordedOptions(
            model=SPEECH_MODEL, 
            language=SPEECH_LANG,
            smart_format=True, 
            punctuate=True, 
            endpointing=500
        )
        response = deepgram.listen.prerecorded.v('1').transcribe_file(source, options)
        transcript = response.results.channels[0].alternatives[0].transcript if response.results else ''
        
        return jsonify({
            'text': transcript, 
            'denoised': ENABLE_DENOISING, 
            'duration': len(audio_data)/sample_rate
        })
    except Exception as e:
        print(f"❌ ASR error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"🎙️ ASR Denoised service on {PORT} | Model: {SPEECH_MODEL} | Denoising: {ENABLE_DENOISING}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
