# ElevenLabs Audio Generation with Blaxel

This setup provides two ways to generate and save audio using ElevenLabs text-to-speech:

## Option 1: Simple Local Generation (`generate-audio.mts`)

Generates audio and saves it locally to an `audio-output` directory.

### Usage
```bash
npx tsx generate-audio.mts "Your text here"
```

### Example
```bash
npx tsx generate-audio.mts "Hello, this is a test of the ElevenLabs API"
```

### Output
- Audio files are saved to `./audio-output/` directory
- Default filenames: `audio-{timestamp}.mp3`

---

## Option 2: Advanced with Blaxel Integration (`blaxel-audio.mts`)

Generates audio and saves it locally, to a Blaxel sandbox, or both.

### Usage
```bash
npx tsx blaxel-audio.mts "<text>" [--local] [--blaxel] [--both]
```

### Flags
- `--local` - Save only to local `audio-output/` directory (default if no flag specified)
- `--blaxel` - Save only to a Blaxel sandbox at `/audio/` directory
- `--both` - Save to both local and Blaxel sandbox

### Examples
```bash
# Save locally (default)
npx tsx blaxel-audio.mts "BINGUS SPOINGUS test"

# Save only to Blaxel sandbox
npx tsx blaxel-audio.mts "Test audio" --blaxel

# Save to both locations
npx tsx blaxel-audio.mts "Test audio" --both
```

### Output
- **Local**: Files saved to `./audio-output/`
- **Blaxel**: Files saved to `/audio/` directory in sandbox named `audio-sandbox`

---

## Configuration

### ElevenLabs Setup
1. Make sure you have `ELEVENLABS_API_KEY` in your `.env` file
2. You can customize the voice ID by editing the `VOICE_ID` variable in the scripts
   - Current: `'JBFqnCBsd6RMkjVDRZzb'`
   - Find other voice IDs at: https://elevenlabs.io/docs/api-reference/voices

### Audio Format
Current settings:
- Model: `eleven_multilingual_v2` (supports 29 languages)
- Output: `mp3_44100_128` (MP3, 44.1kHz, 128kbps)

To change format, edit the `OUTPUT_FORMAT` variable:
- `mp3_44100_128` - MP3, 44.1kHz, 128kbps
- `mp3_22050_32` - MP3, 22.05kHz, 32kbps
- `pcm_22050` - PCM, 22.05kHz
- `ulaw_8000` - µ-law, 8kHz

### Blaxel Sandbox Configuration
Edit the sandbox creation parameters in `blaxel-audio.mts`:
```typescript
const sandbox = await SandboxInstance.createIfNotExists({
    name: sandboxName,        // Sandbox name
    image: "blaxel/nextjs:latest",  // Environment image
    memory: 2048,             // Memory in MB
    region: "us-pdx-1"        // Region
});
```

---

## API Key Setup

Make sure you have a `.env` file in the project root:
```
ELEVENLABS_API_KEY=your_api_key_here
BLAXEL_API_KEY=your_blaxel_key_here  # If using Blaxel features
```

---

## Tips

1. **Check Generated Files**: Navigate to `audio-output/` folder to find saved MP3 files
2. **Use in Blaxel**: Audio saved to Blaxel can be used in further processing within the sandbox
3. **Batch Processing**: You can call these scripts multiple times in a loop for multiple texts
4. **Combine with Blaxel**: Use Blaxel to run additional processing (transcoding, analysis, etc.) on the generated audio

---

## Troubleshooting

- **"No such file or directory"**: Make sure you're running from the `BingusSpoingus/` directory
- **"ELEVENLABS_API_KEY not found"**: Check your `.env` file has the correct API key
- **"Blaxel connection failed"**: Verify your Blaxel credentials in `.env`
