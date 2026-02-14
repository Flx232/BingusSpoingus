/**
 * Text-to-Speech Service Module
 * 
 * This module handles audio generation using ElevenLabs API
 * running inside a Blaxel sandbox.
 */

import { SandboxInstance } from "@blaxel/core";
import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { resolve, join } from 'path';

interface TTSOptions {
    text: string;
    voiceId?: string;
    modelId?: string;
    outputFormat?: string;
    downloadAudio?: boolean;
}

interface TTSResult {
    success: boolean;
    audioPath?: string;
    filename?: string;
    localPath?: string;
    error?: string;
}

const DEFAULT_VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb';
const DEFAULT_MODEL_ID = 'eleven_multilingual_v2';
const DEFAULT_OUTPUT_FORMAT = 'mp3_44100_128';
const LOCAL_OUTPUT_DIR = resolve(process.cwd(), 'audio-output');

export async function generateTextToSpeech(options: TTSOptions): Promise<TTSResult> {
    const {
        text,
        voiceId = DEFAULT_VOICE_ID,
        modelId = DEFAULT_MODEL_ID,
        outputFormat = DEFAULT_OUTPUT_FORMAT,
        downloadAudio = false
    } = options;

    const filename = `audio-${Date.now()}.mp3`;

    try {
        console.log('Creating/connecting to Blaxel sandbox...');
        
        // Create or connect to sandbox
        const sandbox = await SandboxInstance.createIfNotExists({
            name: "tts-sandbox",
            image: "blaxel/node:latest",
            memory: 4096,
            region: "us-pdx-1"
        });

        console.log('✓ Sandbox ready');

        // Create audio directory first
        console.log('Creating /audio directory in sandbox...');
        await sandbox.process.exec({
            name: `mkdir-${Date.now()}`,
            command: 'mkdir -p /audio /workspace'
        });
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Create package.json and install ElevenLabs SDK in the sandbox
        console.log('Setting up Node.js environment in sandbox...');
        
        const packageJson = JSON.stringify({
            name: "tts-generator",
            version: "1.0.0",
            dependencies: {
                "@elevenlabs/elevenlabs-js": "^2.35.0"
            }
        });
        
        await sandbox.fs.write('/workspace/package.json', packageJson);
        
        // Create text-processor.js (teammate will enhance this)
        const textProcessorContent = `
/**
 * Text Processing Module - runs in Blaxel sandbox
 * 
 * TEAMMATE: Add your text processing logic in the processText function below
 */

async function processText(inputText) {
    // ============================================================
    // TEAMMATE: Add your text processing logic here
    // ============================================================
    
    console.log('Processing text:', inputText.substring(0, 50) + '...');
    
    // Example processing steps that could be added:
    // 1. Clean and normalize text
    // 2. Expand abbreviations
    // 3. Add pauses and intonation markers
    // 4. Enhance content (make it longer, add context, etc.)
    // 5. Apply any AI-based text expansion
    
    // For now, just return the original text
    // Your teammate should replace this with actual processing
    let processedText = inputText;
    
    // Example of what processing might look like:
    /*
    processedText = await enhanceText(inputText);
    processedText = await expandContent(processedText);
    processedText = await addIntonation(processedText);
    */
    
    console.log('Processed text:', processedText.substring(0, 50) + '...');
    return processedText;
}

module.exports = { processText };
`;
        
        await sandbox.fs.write('/workspace/text-processor.js', textProcessorContent);
        
        const installProc = await sandbox.process.exec({
            name: `install-${Date.now()}`,
            command: 'cd /workspace && npm install 2>&1'
        });
        
        // Wait for installation and check logs
        await new Promise(resolve => setTimeout(resolve, 15000));
        
        const installLogs = await sandbox.process.logs(installProc.name);
        console.log('Install logs (first 800 chars):', installLogs.substring(0, 800));
        
        if (installLogs.includes('ERR!') || installLogs.includes('error')) {
            console.error('Installation may have failed. Full logs:', installLogs);
        } else {
            console.log('✓ Dependencies installed');
        }

        // Create the Node.js script that will run inside Blaxel
        const scriptContent = `
const { ElevenLabsClient } = require('@elevenlabs/elevenlabs-js');
const { processText } = require('./text-processor');
const fs = require('fs');

async function generateAudio() {
    try {
        console.log('Starting audio generation pipeline...');
        console.log('API Key present:', !!process.env.ELEVENLABS_API_KEY);
        console.log('Input text length:', ${JSON.stringify(text)}.length);
        
        // Step 1: Process the text (teammate's code runs here)
        console.log('\\n=== Step 1: Text Processing ===');
        const processedText = await processText(${JSON.stringify(text)});
        console.log('Processed text length:', processedText.length);
        
        // Step 2: Generate audio with ElevenLabs
        console.log('\\n=== Step 2: Audio Generation ===');
        const elevenlabs = new ElevenLabsClient({
            apiKey: process.env.ELEVENLABS_API_KEY
        });

        console.log('Calling ElevenLabs API...');
        const audio = await elevenlabs.textToSpeech.convert('${voiceId}', {
            text: processedText,
            modelId: '${modelId}',
            outputFormat: '${outputFormat}'
        });

        console.log('Received audio stream, reading chunks...');
        const reader = audio.getReader();
        const chunks = [];
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
        }

        console.log('Concatenating audio chunks...');
        const audioData = Buffer.concat(chunks.map(chunk => Buffer.from(chunk)));
        
        // Save to /audio directory
        console.log('Creating directory if needed...');
        if (!fs.existsSync('/audio')) {
            fs.mkdirSync('/audio', { recursive: true });
        }
        
        console.log('Writing file to /audio/${filename}...');
        fs.writeFileSync('/audio/${filename}', audioData);
        console.log('✓ Audio saved to /audio/${filename}');
        console.log('File size:', audioData.length, 'bytes');
        
        // Verify file was written
        if (fs.existsSync('/audio/${filename}')) {
            console.log('✓ File verified on disk');
        } else {
            console.error('✗ File not found after writing!');
        }
    } catch (error) {
        console.error('Error in generateAudio:', error.message);
        console.error('Stack:', error.stack);
        process.exit(1);
    }
}

generateAudio().catch(err => {
    console.error('Uncaught error:', err);
    process.exit(1);
});
`;

        // Write the script to the workspace
        console.log('Creating TTS script in sandbox...');
        await sandbox.fs.write('/workspace/generate-audio.js', scriptContent);
        console.log('✓ Script created');

        // Execute the script with the API key
        console.log('Generating audio in sandbox...');
        const processName = `tts-${Date.now()}`;
        const execProcess = await sandbox.process.exec({
            name: processName,
            command: `cd /workspace && ELEVENLABS_API_KEY='${process.env.ELEVENLABS_API_KEY}' node generate-audio.js 2>&1`
        });

        // Wait for completion and poll status
        console.log('Waiting for audio generation...');
        let processCompleted = false;
        let attempts = 0;
        const maxAttempts = 15;
        
        while (!processCompleted && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            attempts++;
            
            try {
                const processInfo = await sandbox.process.get(processName);
                console.log(`Attempt ${attempts}: Process status - ${processInfo.status}`);
                
                const status = String(processInfo.status || '').toUpperCase();
                if (status === 'EXITED' || status === 'COMPLETED') {
                    processCompleted = true;
                    console.log('Process completed with exit code:', processInfo.exitCode);
                }
            } catch (err) {
                console.log('Error checking process status:', err);
            }
        }

        // Get process logs
        const logs = await sandbox.process.logs(processName);
        console.log('--- Sandbox Output ---');
        console.log(logs);
        console.log('--- End Output ---');

        // Verify the file exists
        console.log('Verifying audio file...');
        
        // Check if directory exists first
        let files: string[] = [];
        try {
            const lsResult = await sandbox.fs.ls('/audio');
            const entries = Array.isArray(lsResult.files) ? lsResult.files : [];
            files = entries.map((entry: any) => {
                if (typeof entry === 'string') return entry;
                return entry?.name || entry?.path || '';
            }).filter((name: string) => name.length > 0);
        } catch (err: any) {
            console.error('Error listing /audio directory:', err.message);
            return {
                success: false,
                error: `Failed to access /audio directory: ${err.message}. Process logs: ${logs}`
            };
        }
        
        const fileMatch = files.some((name) => name === filename || name.endsWith(`/${filename}`));
        if (!fileMatch) {
            console.error('✗ Audio file not found');
            console.error('Expected filename:', filename);
            console.error('Available files in /audio:', files);
            console.error('Process logs:', logs);
            return {
                success: false,
                error: `Audio file was not created in sandbox. Expected: ${filename}. Found: ${files.join(', ') || 'none'}. Logs: ${logs.substring(0, 500)}`
            };
        }

        console.log(`✓ Audio file created successfully: /audio/${filename}`);

        const result: TTSResult = {
            success: true,
            audioPath: `/audio/${filename}`,
            filename: filename
        };

        // Download audio to local machine if requested
        if (downloadAudio) {
            console.log('🔽 Downloading audio to local machine...');
            console.log(`   Reading from sandbox: /audio/${filename}`);
            
            if (!existsSync(LOCAL_OUTPUT_DIR)) {
                console.log(`   Creating directory: ${LOCAL_OUTPUT_DIR}`);
                await mkdir(LOCAL_OUTPUT_DIR, { recursive: true });
                console.log('   ✓ Directory created');
            } else {
                console.log(`   Directory already exists: ${LOCAL_OUTPUT_DIR}`);
            }
            
            const localPath = join(LOCAL_OUTPUT_DIR, filename);
            console.log(`   Writing file to: ${localPath}`);
            await sandbox.fs.download(`/audio/${filename}`, localPath);
            console.log(`   ✓ File written successfully!`);
            console.log(`\n📁 Audio saved to: ${localPath}\n`);
            
            result.localPath = localPath;
        } else {
            console.log('ℹ️  downloadAudio=false, skipping local download');
            console.log(`   Audio is available in sandbox at: /audio/${filename}`);
        }

        return result;

    } catch (error: any) {
        console.error('TTS generation error:', error);
        return {
            success: false,
            error: error.message || 'Unknown error occurred'
        };
    }
}
