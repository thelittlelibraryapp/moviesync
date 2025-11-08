/**
 * AudioRecorder - Web Audio API microphone recording
 * Records 10 seconds of audio and converts to WAV format for fingerprinting
 */

class AudioRecorder {
  constructor() {
    this.audioContext = null;
    this.mediaStream = null;
    this.mediaStreamSource = null;
    this.recorder = null;
    this.audioChunks = [];
    this.recording = false;
  }

  /**
   * Request microphone permission from user
   */
  async requestPermission() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      return { success: true, stream };
    } catch (error) {
      let errorMessage = "Microphone access denied.";

      if (error.name === "NotAllowedError") {
        errorMessage = "Microphone access needed to identify movies. Please allow microphone access.";
      } else if (error.name === "NotFoundError") {
        errorMessage = "No microphone found. Please check your device.";
      } else if (error.name === "NotReadableError") {
        errorMessage = "Microphone busy. Close other apps using it.";
      }

      return { success: false, error: errorMessage };
    }
  }

  /**
   * Start recording audio
   * @param {number} duration - Recording duration in seconds (default 10)
   * @param {function} onProgress - Callback for progress updates
   */
  async startRecording(duration = 10, onProgress = null) {
    try {
      // Request microphone access
      const permissionResult = await this.requestPermission();
      if (!permissionResult.success) {
        throw new Error(permissionResult.error);
      }

      this.mediaStream = permissionResult.stream;
      this.audioChunks = [];

      // Create AudioContext
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
      });

      // Create MediaRecorder
      const options = { mimeType: 'audio/webm' };
      this.recorder = new MediaRecorder(this.mediaStream, options);

      this.recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      // Start recording
      this.recorder.start();
      this.recording = true;

      // Progress updates
      if (onProgress) {
        const interval = setInterval(() => {
          if (!this.recording) {
            clearInterval(interval);
          }
        }, 100);
      }

      // Auto-stop after duration
      return new Promise((resolve, reject) => {
        setTimeout(async () => {
          try {
            const result = await this.stopRecording();
            resolve(result);
          } catch (error) {
            reject(error);
          }
        }, duration * 1000);
      });

    } catch (error) {
      this.cleanup();
      throw new Error(`Recording failed: ${error.message}`);
    }
  }

  /**
   * Stop recording and return audio data
   */
  async stopRecording() {
    return new Promise((resolve, reject) => {
      if (!this.recorder || !this.recording) {
        reject(new Error("No active recording"));
        return;
      }

      this.recorder.onstop = async () => {
        try {
          // Create blob from recorded chunks
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

          // Convert to WAV
          const wavData = await this.convertToWav(audioBlob);

          // Encode as base64
          const base64Audio = await this.encodeBase64(wavData);

          this.cleanup();
          resolve({ success: true, audio: base64Audio });
        } catch (error) {
          this.cleanup();
          reject(new Error(`Failed to process audio: ${error.message}`));
        }
      };

      this.recorder.stop();
      this.recording = false;
    });
  }

  /**
   * Convert audio blob to WAV format
   */
  async convertToWav(audioBlob) {
    try {
      // Create audio buffer from blob
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

      // Convert to WAV
      const wavBuffer = this.audioBufferToWav(audioBuffer);
      return new Blob([wavBuffer], { type: 'audio/wav' });
    } catch (error) {
      throw new Error(`WAV conversion failed: ${error.message}`);
    }
  }

  /**
   * Convert AudioBuffer to WAV format
   */
  audioBufferToWav(audioBuffer) {
    const numOfChannels = 1; // Mono
    const sampleRate = audioBuffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;

    const channelData = audioBuffer.getChannelData(0);
    const samples = new Int16Array(channelData.length);

    // Convert float samples to 16-bit PCM
    for (let i = 0; i < channelData.length; i++) {
      const sample = Math.max(-1, Math.min(1, channelData[i]));
      samples[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
    }

    const dataLength = samples.length * 2;
    const buffer = new ArrayBuffer(44 + dataLength);
    const view = new DataView(buffer);

    // Write WAV header
    this.writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataLength, true);
    this.writeString(view, 8, 'WAVE');
    this.writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // Subchunk1Size
    view.setUint16(20, format, true);
    view.setUint16(22, numOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numOfChannels * bitDepth / 8, true);
    view.setUint16(32, numOfChannels * bitDepth / 8, true);
    view.setUint16(34, bitDepth, true);
    this.writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);

    // Write audio data
    const offset = 44;
    for (let i = 0; i < samples.length; i++) {
      view.setInt16(offset + i * 2, samples[i], true);
    }

    return buffer;
  }

  /**
   * Write string to DataView
   */
  writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  /**
   * Encode blob as base64
   */
  async encodeBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        // Remove data URL prefix
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  /**
   * Clean up resources
   */
  cleanup() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.recorder = null;
    this.audioChunks = [];
    this.recording = false;
  }
}

export default AudioRecorder;
