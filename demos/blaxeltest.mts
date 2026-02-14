import { SandboxInstance } from "@blaxel/core";

async function main() {
  // Create a new sandbox
    const sandbox = await SandboxInstance.createIfNotExists({
        name: "my-sandbox",
        image: "blaxel/nextjs:latest",   // public or custom image
        memory: 4096,   // in MB
        ports: [{ target: 3000, protocol: "HTTP" }],   // ports to expose
        region: "us-pdx-1"   // if not specified, Blaxel will choose a default region
    });
    console.log("Sandbox created:", {sandbox});
  
  /// ADD REST OF CODE HERE
  // List files in a directory
    const { subdirectories, files } = await sandbox.fs.ls("/");
    console.log("Files:", {files}, "Subdirectories:", {subdirectories});

    // Run a command
    const process = await sandbox.process.exec({
    name: "hello-process",
    command: "echo 'Hello, World!'"
    });
    const processInfo = await sandbox.process.get("hello-process");

    // Get logs (in batch)
    const logs = await sandbox.process.logs("hello-process");
    console.log("Logs:", {logs});
}

main().catch(console.error);