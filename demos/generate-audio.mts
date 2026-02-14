import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';
import { writeFile } from 'fs/promises';
import { resolve } from 'path';
import 'dotenv/config';

const elevenlabs = new ElevenLabsClient({
    apiKey: process.env.ELEVENLABS_API_KEY,
});

// Configuration
const VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb'; // Replace with desired voice ID
const OUTPUT_DIR = './audio-output'; // Directory to save audio files
const MODEL_ID = 'eleven_multilingual_v2';
const OUTPUT_FORMAT = 'mp3_44100_128';

async function generateAudio(text: string, filename?: string): Promise<string> {
    try {
        console.log(`Generating audio for: "${text.substring(0, 50)}..."`);
        
        // Convert text to speech
        const audio = await elevenlabs.textToSpeech.convert(VOICE_ID, {
            text,
            modelId: MODEL_ID,
            outputFormat: OUTPUT_FORMAT,
        });

        // Read audio data into buffer
        const reader = audio.getReader();
        const chunks: Uint8Array[] = [];
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
        }

        // Combine chunks into single buffer
        const audioData = Buffer.concat(chunks.map(chunk => Buffer.from(chunk)));

        // Generate filename if not provided
        const outputFilename = filename || `audio-${Date.now()}.mp3`;
        const outputPath = resolve(OUTPUT_DIR, outputFilename);

        // Create output directory if it doesn't exist
        const fs = await import('fs');
        if (!fs.existsSync(OUTPUT_DIR)) {
            await import('fs/promises').then(fsp => fsp.mkdir(OUTPUT_DIR, { recursive: true }));
        }

        // Save audio to file
        await writeFile(outputPath, audioData);
        console.log(`✓ Audio saved to: ${outputPath}`);

        return outputPath;
    } catch (error) {
        console.error('Error generating audio:', error);
        throw error;
    }
}

// Main execution
async function main() {
    // Get text from command line arguments
    const textInput = process.argv.slice(2).join(' ');
    
    if (!textInput) {
        console.error('Usage: npx tsx generate-audio.mts <text to convert>');
        console.error('Example: npx tsx generate-audio.mts "Hello, this is a test"');
        process.exit(1);
    }

    try {
        await generateAudio(textInput);
    } catch (error) {
        console.error('Failed to generate audio:', error);
        process.exit(1);
    }
}

main();
