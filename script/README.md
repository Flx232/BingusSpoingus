# Podcast Scripts

This folder contains generated podcast scripts created by the BingusSpoingus pipeline.

## File Naming Convention

Scripts are saved with the following format:
```
podcast_{query}_{timestamp}.md
```

Where:
- `{query}` - First 30 characters of the search query (spaces replaced with underscores)
- `{timestamp}` - Generation time in format `YYYYMMDD_HHMMSS`

## Script Format

Each script contains:
- **Metadata**: Episode type, length, tone, target audience, and sources
- **Full Script**: Complete podcast script with speaker labels and production notes
- **Source References**: List of all web sources used

## Usage

Generated scripts can be:
1. Read directly by a human narrator
2. Converted to audio using text-to-speech services (like ElevenLabs)
3. Used as a base for further editing and production