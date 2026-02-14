import { SandboxInstance } from "@blaxel/core";

const sandboxName = "audio-sandbox"

async function main() {
  try {
    // Retrieve the sandbox
    const sandbox = await SandboxInstance.get(sandboxName)

    // Test filesystem
    const dir = await sandbox.fs.ls("/audio");
    console.log(dir.files);

    // Test process
    const process = await sandbox.process.exec({
      name: "test",
      command: "echo 'Hello world'",
    });
    await new Promise((resolve) => setTimeout(resolve, 10));

    // Retrieve process logs
    const logs = await sandbox.process.logs("test");
    console.log("Logs:", {logs});
  } catch (e) {
    console.error("There was an error => ", e);
  }
}

main()
  .catch((err) => {
    console.error("There was an error => ", err);
    process.exit(1);
  })
  .then(() => {
    process.exit(0);
  })