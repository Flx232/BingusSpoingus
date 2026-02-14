/**
 * Test Client for TTS Agent
 * 
 * This script tests the TTS agent by sending requests to it.
 * Run the agent first with: npx tsx watch src/index.ts
 * Then run this in another terminal: npx tsx test-client.ts
 */

const AGENT_URL = 'http://localhost:80';

interface TTSResponse {
    success: boolean;
    message?: string;
    audioPath?: string;
    filename?: string;
    localPath?: string;
    text?: string;
    error?: string;
}

async function testHealthCheck() {
    console.log('Testing health check endpoint...');
    try {
        const response = await fetch(`${AGENT_URL}/health`);
        const data = await response.json();
        console.log('✓ Health check:', data);
        return true;
    } catch (error: any) {
        console.error('✗ Health check failed:', error.message);
        return false;
    }
}

async function testTTSGeneration(text: string, downloadAudio: boolean = false) {
    console.log(`\nTesting TTS generation...`);
    console.log(`Input: "${text}"`);
    console.log(`Download: ${downloadAudio}`);
    console.log('─'.repeat(60));

    try {
        const response = await fetch(`${AGENT_URL}/generate-audio`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text,
                downloadAudio
            })
        });

        const data: TTSResponse = await response.json();
        
        if (data.success) {
            console.log('✓ Audio generated successfully!');
            console.log('  - Audio Path (in sandbox):', data.audioPath);
            console.log('  - Filename:', data.filename);
            if (data.localPath) {
                console.log('  - Local Path:', data.localPath);
            }
            console.log('  - Processed Text:', data.text);
        } else {
            console.log('✗ Failed to generate audio');
            console.log('  - Error:', data.error);
        }
        
        return data;
    } catch (error: any) {
        console.error('✗ Request failed:', error.message);
        return null;
    }
}

async function main() {
    console.log('🎙️  TTS Agent Test Client');
    console.log('═'.repeat(60));
    
    // Test 1: Health check
    const healthy = await testHealthCheck();
    if (!healthy) {
        console.error('\n⚠️  Agent is not running. Start it with: npx tsx watch src/index.ts');
        process.exit(1);
    }

    // Test 2: Generate audio (no download)
    await testTTSGeneration('weeee wwooooooo AWAWAAAAAAAAAAWWAAAAAAAA', true);

    // // Test 3: Generate audio with download
    // await testTTSGeneration('This is another test with local download enabled.', true);

    // // Test 4: Longer text
    // await testTTSGeneration(
    //     'WAUW uHUEHUHUHUHUHHU AAAAAAAaaaAAAAaaaAAb MOMMYYYYY I AM A BINGUS SPOINGUuUUUS!!! BINGUS SPOINGUS BINGUS SPOINGUS',
    //     false
    // );

    console.log('\n' + '═'.repeat(60));
    console.log('✓ All tests complete!');
}

main().catch(console.error);
