import { SandboxInstance } from "@blaxel/core";
import 'dotenv/config';

interface TTSOptions {
    text: string;
    voiceId?: string;
    modelId?: string;
    outputFormat?: string;
    filename?: string;
}

async function textToSpeechInBlaxel(options: TTSOptions) {
    const {
        text,
        voiceId = 'JBFqnCBsd6RMkjVDRZzb',
        modelId = 'eleven_multilingual_v2',
        outputFormat = 'mp3_44100_128',
        filename = `audio-${Date.now()}.mp3`
    } = options;

    console.log('Creating/connecting to Blaxel sandbox...');
    
    // Create or connect to sandbox
    const sandbox = await SandboxInstance.createIfNotExists({
        name: "tts-sandbox",
        image: "blaxel/nodejs:latest",
        memory: 4096,
        region: "us-pdx-1"
    });

    console.log('✓ Sandbox ready');

    // Install ElevenLabs SDK in the sandbox
    console.log('Installing ElevenLabs SDK in sandbox...');
    const installProcess = await sandbox.process.exec({
        name: `install-${Date.now()}`,
        command: 'npm install @elevenlabs/elevenlabs-js'
    });
    
    // Wait for installation to complete
    await new Promise(resolve => setTimeout(resolve, 5000));
    console.log('✓ Dependencies installed');

    // Create the Node.js script that will run inside Blaxel
    const scriptContent = `
const { ElevenLabsClient } = require('@elevenlabs/elevenlabs-js');
const fs = require('fs');

async function generateAudio() {
    try {
        const elevenlabs = new ElevenLabsClient({
            apiKey: process.env.ELEVENLABS_API_KEY
        });

        console.log('Generating audio...');
        const audio = await elevenlabs.textToSpeech.convert('${voiceId}', {
            text: ${JSON.stringify(text)},
            modelId: '${modelId}',
            outputFormat: '${outputFormat}'
        });

        const reader = audio.getReader();
        const chunks = [];
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
        }

        const audioData = Buffer.concat(chunks.map(chunk => Buffer.from(chunk)));
        
        // Save to /audio directory
        if (!fs.existsSync('/audio')) {
            fs.mkdirSync('/audio', { recursive: true });
        }
        
        fs.writeFileSync('/audio/${filename}', audioData);
        console.log('Audio saved to /audio/${filename}');
        console.log('Size:', audioData.length, 'bytes');
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

generateAudio();
`;

    // Write the script to the sandbox
    console.log('Creating TTS script in sandbox...');
    await sandbox.fs.write('/tmp/generate-audio.js', scriptContent);
    console.log('✓ Script created');

    // Execute the script with the API key
    console.log('Generating audio in sandbox...');
    const execProcess = await sandbox.process.exec({
        name: `tts-${Date.now()}`,
        command: `ELEVENLABS_API_KEY=${process.env.ELEVENLABS_API_KEY} node /tmp/generate-audio.js`
    });

    // Wait for completion and get logs
    await new Promise(resolve => setTimeout(resolve, 8000));
    const logs = await sandbox.process.logs(execProcess.name);
    console.log('\n--- Sandbox Output ---');
    console.log(logs);
    console.log('--- End Output ---\n');

    // Verify the file exists
    console.log('Verifying audio file...');
    const { files } = await sandbox.fs.ls('/audio');
    
    if (files.includes(filename)) {
        console.log(`✓ Audio file created successfully: /audio/${filename}`);
        console.log(`\nTo download the file, use:`);
        console.log(`  const audioData = await sandbox.fs.read('/audio/${filename}');`);
        return {
            success: true,
            path: `/audio/${filename}`,
            sandbox: sandbox,
            filename: filename
        };
    } else {
        console.log('✗ Audio file not found');
        console.log('Available files in /audio:', files);
        return {
            success: false,
            error: 'Audio file was not created'
        };
    }
}

// Optional: Download audio from sandbox to local machine
async function downloadAudio(sandbox: SandboxInstance, remotePath: string, localPath: string) {
    console.log(`\nDownloading ${remotePath} to ${localPath}...`);
    const audioData = await sandbox.fs.read(remotePath);
    
    const fs = await import('fs/promises');
    const { dirname } = await import('path');
    const dir = dirname(localPath);
    
    // Create directory if it doesn't exist
    const fsSync = await import('fs');
    if (!fsSync.existsSync(dir)) {
        await fs.mkdir(dir, { recursive: true });
    }
    
    await fs.writeFile(localPath, audioData);
    console.log(`✓ Downloaded to ${localPath}`);
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('Usage: npx tsx blaxel-tts.mts "<text>" [--download]');
        console.error('');
        console.error('Examples:');
        console.error('  npx tsx blaxel-tts.mts "Hello world"');
        console.error('  npx tsx blaxel-tts.mts "Hello world" --download');
        console.error('');
        console.error('Options:');
        console.error('  --download    Download the audio file to local ./audio-output directory');
        process.exit(1);
    }

    const shouldDownload = args.includes('--download');
    const text = args.filter(arg => !arg.startsWith('--')).join(' ');

    console.log(`\n🎙️  Text-to-Speech with Blaxel`);
    console.log(`Input: "${text}"`);
    console.log('─'.repeat(50));

    try {
        const result = await textToSpeechInBlaxel({ text });
        
        if (result.success && shouldDownload) {
            const localPath = `./audio-output/${result.filename}`;
            await downloadAudio(result.sandbox, result.path!, localPath);
        }

        console.log('\n' + '─'.repeat(50));
        console.log('✓ Complete!');
    } catch (error) {
        console.error('\n✗ Error:', error);
        process.exit(1);
    }
}

main();
