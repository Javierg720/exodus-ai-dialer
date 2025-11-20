const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 6011;
const VOICE = process.env.VOICE || 'en-US-AvaMultilingualNeural';
const RATE = process.env.RATE || '+10%';
const PITCH = process.env.PITCH || '+2Hz';

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    provider: 'edge-tts',
    voice: VOICE,
    cost: 'FREE'
  });
});

// Main TTS endpoint - Returns raw LINEAR16 PCM at 8kHz for AudioSocket compatibility
app.post('/text-to-speech-stream', async (req, res) => {
  try {
    const { text } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    console.log(`[Edge TTS] Generating audio for: "${text.substring(0, 50)}..."`);

    // Create temporary files
    const wavFile = path.join('/tmp', `tts_${Date.now()}.wav`);
    const rawFile = path.join('/tmp', `tts_${Date.now()}.raw`);

    // Build edge-tts command
    const args = [
      '--text', text,
      '--voice', VOICE,
      '--rate', RATE,
      '--pitch', PITCH,
      '--write-media', wavFile
    ];

    const edgeTTS = spawn('edge-tts', args);

    let errorOutput = '';

    edgeTTS.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    edgeTTS.on('close', (code) => {
      if (code !== 0) {
        console.error('[Edge TTS] Error:', errorOutput);
        res.status(500).json({
          error: 'TTS generation failed',
          details: errorOutput
        });
        return;
      }

      // Convert WAV to raw LINEAR16 PCM at 8kHz using ffmpeg
      const ffmpeg = spawn('ffmpeg', [
        '-i', wavFile,
        '-f', 's16le',        // signed 16-bit little-endian
        '-acodec', 'pcm_s16le',
        '-ar', '8000',        // 8kHz sample rate (required for AudioSocket)
        '-ac', '1',           // mono
        rawFile
      ]);

      let ffmpegError = '';
      ffmpeg.stderr.on('data', (data) => {
        ffmpegError += data.toString();
      });

      ffmpeg.on('close', (ffmpegCode) => {
        // Clean up WAV file immediately
        fs.unlink(wavFile, (err) => {
          if (err) console.error('[Edge TTS] Failed to delete WAV file:', err);
        });

        if (ffmpegCode !== 0) {
          console.error('[Edge TTS] FFmpeg conversion error:', ffmpegError);
          res.status(500).json({
            error: 'Audio conversion failed',
            details: ffmpegError
          });
          return;
        }

        console.log('[Edge TTS] Converted to 8kHz LINEAR16 PCM');

        // Stream raw PCM audio back
        res.setHeader('Content-Type', 'application/octet-stream');

        const audioStream = fs.createReadStream(rawFile);

        audioStream.pipe(res);

        audioStream.on('end', () => {
          // Clean up temp file
          fs.unlink(rawFile, (err) => {
            if (err) console.error('[Edge TTS] Failed to delete raw file:', err);
          });
        });

        audioStream.on('error', (err) => {
          console.error('[Edge TTS] Stream error:', err);
          res.status(500).json({ error: 'Audio streaming failed' });
        });
      });
    });

  } catch (error) {
    console.error('[Edge TTS] Error:', error.message);
    res.status(500).json({
      error: error.message,
      provider: 'edge-tts'
    });
  }
});

// List available voices
app.get('/voices', async (req, res) => {
  try {
    const edgeTTS = spawn('edge-tts', ['--list-voices']);

    let output = '';
    edgeTTS.stdout.on('data', (data) => {
      output += data.toString();
    });

    edgeTTS.on('close', () => {
      res.json({ voices: output.split('\n').filter(v => v.trim()) });
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[Edge TTS Provider] Running on port ${PORT}`);
  console.log(`[Edge TTS] Voice: ${VOICE}`);
  console.log(`[Edge TTS] Rate: ${RATE}, Pitch: ${PITCH}`);
  console.log(`[Edge TTS] Cost: FREE!`);
});
