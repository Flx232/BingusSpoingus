# Blaxel Agent Template (TypeScript)

<p align="center">
  <img src="https://blaxel.ai/logo.png" alt="Blaxel" width="200"/>
</p>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js 18+](https://img.shields.io/badge/node-18+-blue.svg)](https://nodejs.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-enabled-blue.svg)](https://www.typescriptlang.org/)

</div>

A minimal TypeScript template for a Blaxel-hosted agent. It includes a tiny Fastify HTTP server, optional telemetry, and ready-to-use scripts for local development and deployment on Blaxel.

## 📑 Table of Contents

- [Blaxel Agent Template (TypeScript)](#blaxel-agent-template-typescript)
  - [📑 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🚀 Quick Start](#-quick-start)
  - [📋 Prerequisites](#-prerequisites)
  - [💻 Installation](#-installation)
  - [🔧 Usage](#-usage)
    - [Running the Server Locally](#running-the-server-locally)
    - [Testing your agent](#testing-your-agent)
    - [Deploying to Blaxel](#deploying-to-blaxel)
  - [📁 Project Structure](#-project-structure)
  - [❓ Troubleshooting](#-troubleshooting)
    - [Common Issues](#common-issues)
  - [👥 Contributing](#-contributing)
  - [🆘 Support](#-support)
  - [📄 License](#-license)

## ✨ Features

- Minimal Fastify server (Hello World)
- TypeScript-first setup with IDE support
- Optional Blaxel telemetry wired in
- Hot reload for local development
- One-command deploy to Blaxel

## 🚀 Quick Start

For those who want to get up and running quickly:

```bash
# Clone the repository
git clone https://github.com/blaxel-templates/template-blank-ts.git

# Navigate to the project directory
cd template-blank-ts

# Install dependencies
npm install

# Start the server (hot reload)
bl serve --hotreload
```

## 📋 Prerequisites

- **Node.js:** 18.0 or later
- **NPM:** Node package manager
- **Blaxel Platform Setup:** Complete Blaxel setup by following the Quickstart
  - **Blaxel CLI:** Ensure you have the Blaxel CLI installed. If not, install it globally:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/blaxel-ai/toolkit/main/install.sh | BINDIR=/usr/local/bin sudo -E sh
    ```
  - **Blaxel login:** Login to Blaxel platform
    ```bash
    bl login YOUR-WORKSPACE
    ```

## 💻 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/blaxel-templates/template-blank-ts.git
cd template-blank-ts
npm install
```

## 🔧 Usage

### Running the Server Locally

Start the development server with hot reloading:

```bash
bl serve --hotreload
```

The server listens on the host and port provided by Blaxel, already implemented in `src/index.ts`:

```ts
const port = parseInt(process.env.PORT || "80");
const host = process.env.HOST || "0.0.0.0";
```

### Testing your agent

You can test your agent with curl:

```bash
curl -X POST http://127.0.0.1:8080/ \
  -H "content-type: application/json" \
  -d '{"inputs":"hello"}'
```

### Deploying to Blaxel

When you are ready to deploy your application:

```bash
bl deploy
```

This will package your code using your configuration and deploy it as a serverless endpoint on Blaxel. See the Quickstart for details: https://docs.blaxel.ai/Agents/Quickstart-agent

## 📁 Project Structure

- **src/index.ts** - Application entry point and HTTP route(s)
- **package.json** - Node.js package configuration and scripts
- **tsconfig.json** - TypeScript configuration
- **blaxel.toml** - Blaxel deployment configuration

## ❓ Troubleshooting

### Common Issues

1. **Blaxel Platform Issues**:
   - Ensure you're logged in to your workspace: `bl login MY-WORKSPACE`
   - Verify deployment: `bl deploy` outputs an endpoint URL in the console

2. **Node.js Version Issues**:
   - Make sure you have Node.js 18+
   - Try `node --version` to check your version
   - Update Node.js if needed

3. **TypeScript Compilation Errors**:
   - Run `npm run build` to check for type errors
   - Ensure your types match route handlers

4. **Local Serve Issues**:
   - If port 8080 is taken, specify a different port: `bl serve --port 8081`
   - Check console logs for Fastify startup errors

## 👥 Contributing

Contributions are welcome! Here's how you can contribute:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Submit** a Pull Request

Please make sure to follow the TypeScript code style of the project.

## 🆘 Support

If you need help with this template:

- [Submit an issue](https://github.com/blaxel-templates/template-blank-ts/issues) for bug reports or feature requests
- Visit the [Blaxel Documentation](https://docs.blaxel.ai) for platform guidance
- Join our [Discord Community](https://discord.gg/G3NqzUPcHP) for real-time assistance

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
