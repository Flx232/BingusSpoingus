import '@blaxel/telemetry';
import Fastify from "fastify";
import { generateTextToSpeech } from './tts-service';
import 'dotenv/config';
import { error } from 'console';

interface TTSRequestBody {
  text: string;
  voiceId?: string;
  downloadAudio?: boolean;
}

interface RequestBody {
  inputs: string;
}

async function main() {
  console.info("Booting up TTS Agent...");
  const app = Fastify();

  app.addHook("onResponse", async (request, reply) => {
    console.info(`${request.method} ${request.url} ${reply.statusCode} ${Math.round(reply.elapsedTime)}ms`);
  });

  app.addHook("onError", async (request, reply, error) => {
    console.error(error);
  });

  // Health check endpoint
  app.get("/health", async (request, reply) => {
    return reply.send({ status: "healthy", service: "tts-agent" });
  });

  // Main TTS endpoint - this is where the magic happens
  app.post<{ Body: TTSRequestBody }>("/generate-audio", async (request, reply) => {
    try {
      const { text, voiceId, downloadAudio = false } = request.body;

      if (!text) {
        return reply.code(400).send({ error: "Text is required" });
      }

      console.info(`Received TTS request: "${text.substring(0, 50)}..."`);

      // Send text to Blaxel for processing AND audio generation
      // Everything happens in the sandbox now!
      console.info("Sending to Blaxel sandbox for processing and audio generation...");
      const result = await generateTextToSpeech({
        text: text,  // Raw text - will be processed in Blaxel
        voiceId,
        downloadAudio
      });

      if (!result.success) {
        return reply.code(500).send({ error: result.error });
      }

      // Step 3: Return the result
      return reply.send({
        success: true,
        message: "Audio generated successfully (processed and generated in Blaxel)",
        audioPath: result.audioPath,
        filename: result.filename,
        localPath: result.localPath,
        processedInBlaxel: true
      });
    } catch (error: any) {
      console.error("TTS generation error:", error);
      return reply.code(500).send({ 
        error: "Failed to generate audio",
        details: error.message 
      });
    }
  });

  // Original endpoint for compatibility
  app.post<{ Body: RequestBody }>("/", async (request, reply) => {
    return reply.send("Hello World");
  });

  const port = parseInt(process.env.PORT || "80");
  const host = process.env.HOST || "0.0.0.0";

  await app.listen({ port, host });
  console.info(`Server is running on port ${host}:${port}`);
}

main().catch(console.error);
