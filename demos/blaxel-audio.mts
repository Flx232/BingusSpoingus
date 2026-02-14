import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';
import { SandboxInstance } from "@blaxel/core";
import { writeFile } from 'fs/promises';
import { resolve } from 'path';
import 'dotenv/config';

const elevenlabs = new ElevenLabsClient({
    apiKey: process.env.ELEVENLABS_API_KEY,
});

// Configuration
const VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb';
const MODEL_ID = 'eleven_multilingual_v2';
const OUTPUT_FORMAT = 'mp3_44100_128';
const LOCAL_OUTPUT_DIR = './audio-output';
const REMOTE_OUTPUT_DIR = '/audio'; // Directory in Blaxel sandbox

interface AudioOptions {
    saveLocal?: boolean;
    saveToBlaxel?: boolean;
    sandboxName?: string;
}

async function generateAudio(text: string, filename?: string, options: AudioOptions = {}): Promise<{ localPath?: string; remotePath?: string }> {
    const { saveLocal = true, saveToBlaxel = false, sandboxName = 'audio-sandbox' } = options;
    
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

        const audioData = Buffer.concat(chunks.map(chunk => Buffer.from(chunk)));
        const outputFilename = filename || `audio-${Date.now()}.mp3`;
        const results: { localPath?: string; remotePath?: string } = {};

        // Save locally
        if (saveLocal) {
            const fs = await import('fs');
            if (!fs.existsSync(LOCAL_OUTPUT_DIR)) {
                await import('fs/promises').then(fsp => fsp.mkdir(LOCAL_OUTPUT_DIR, { recursive: true }));
            }
            const localPath = resolve(LOCAL_OUTPUT_DIR, outputFilename);
            await writeFile(localPath, audioData);
            console.log(`✓ Audio saved locally to: ${localPath}`);
            results.localPath = localPath;
        }

        // Save to Blaxel sandbox
        if (saveToBlaxel) {
            try {
                const sandbox = await SandboxInstance.createIfNotExists({
                    name: sandboxName,
                    image: "blaxel/nextjs:latest",
                    memory: 2048,
                    region: "us-pdx-1"
                });

                // Ensure directory exists in sandbox
                await sandbox.process.exec({
                    name: `mkdir-${Date.now()}`,
                    command: `mkdir -p ${REMOTE_OUTPUT_DIR}`
                });

                // Write audio file to sandbox
                const base64Audio = audioData.toString('base64');
                await sandbox.process.exec({
                    name: `write-audio-${Date.now()}`,
                    command: `echo ${base64Audio} | base64 -d > ${REMOTE_OUTPUT_DIR}/${outputFilename}`
                });

                const remotePath = `${REMOTE_OUTPUT_DIR}/${outputFilename}`;
                console.log(`✓ Audio saved to Blaxel sandbox: ${remotePath}`);
                results.remotePath = remotePath;
            } catch (error) {
                console.error('Failed to save to Blaxel:', error);
            }
        }

        return results;
    } catch (error) {
        console.error('Error generating audio:', error);
        throw error;
    }
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('Usage: npx tsx blaxel-audio.mts <text> [--local] [--blaxel] [--both]');
        console.error('Examples:');
        console.error('  npx tsx blaxel-audio.mts "Hello world"                  (saves locally)');
        console.error('  npx tsx blaxel-audio.mts "Hello world" --local          (saves locally)');
        console.error('  npx tsx blaxel-audio.mts "Hello world" --blaxel         (saves to Blaxel)');
        console.error('  npx tsx blaxel-audio.mts "Hello world" --both           (saves both)');
        process.exit(1);
    }

    // Parse arguments
    const flags = args.filter(arg => arg.startsWith('--'));
    const text = args.filter(arg => !arg.startsWith('--')).join(' ');

    let saveLocal = true;
    let saveToBlaxel = false;

    if (flags.includes('--local')) {
        saveLocal = true;
        saveToBlaxel = false;
    } else if (flags.includes('--blaxel')) {
        saveLocal = false;
        saveToBlaxel = true;
    } else if (flags.includes('--both')) {
        saveLocal = true;
        saveToBlaxel = true;
    }

    try {
        const result = await generateAudio(text, undefined, { saveLocal, saveToBlaxel });
        console.log('\n✓ Audio generation complete!');
        console.log('Results:', result);
    } catch (error) {
        console.error('Failed to generate audio:', error);
        process.exit(1);
    }
}

main();
