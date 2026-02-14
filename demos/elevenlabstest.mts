import { ElevenLabsClient, play } from '@elevenlabs/elevenlabs-js';
import { Readable } from 'stream';
import 'dotenv/config';

const elevenlabs = new ElevenLabsClient({
    apiKey: process.env.ELEVENLABS_API_KEY,
});

const audio = await elevenlabs.textToSpeech.convert('JBFqnCBsd6RMkjVDRZzb', {
  text: 'WAUW uHUEHUHUHUHUHHU AAAAAAAaaaAAAAaaaAAb MOMMYYYYY I AM A BINGUS SPOINGUuUUUS!!! BINGUS SPOINGUS BINGUS SPOINGUS',
  modelId: 'eleven_multilingual_v2',
  outputFormat: 'mp3_44100_128',
});

const reader = audio.getReader();
const stream = new Readable({
  async read() {
    const { done, value } = await reader.read();
    if (done) {
      this.push(null);
    } else {
      this.push(value);
    }
  },
});

await play(stream);

