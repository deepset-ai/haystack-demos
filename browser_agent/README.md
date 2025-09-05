# 🕵️🌐  Browser Agent

This demo shows how to deploy a Browser Agent with [Docker Compose](https://docs.docker.com/compose/).

Watch it in action as it finds public transportation options from Paris to Berlin:

![Browser Agent](video.gif)

> **Note**: The browser runs in Docker in **headless mode** - you won't see a browser window opening on your screen, but the agent can still interact with websites. See [Running the Browser in headed mode](#running-the-browser-in-headed-mode).


## 🚀 Quickstart

### 1️⃣ Clone the Repository
```sh
git clone git@github.com:deepset-ai/haystack-demos.git
cd haystack-demos/browser_agent
```

### 2️⃣ Export the Google API Key

To get a free Gemini API key, visit [Google AI Studio](https://ai.google.dev/studio).
```sh
export GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
```

### 3️⃣ Build and Run the Containers
```sh
docker-compose up
```


### 4️⃣ Open the Open WebUI User Interface
Open your browser to [http://localhost:3000/](http://localhost:3000/) and start interacting with the Agent.



## 📖 Overview
The Agent is built with Haystack, Google Gemini 2.5 Flash model, and the Playwright MCP server for browser automation.
Take a look at [this notebook](https://haystack.deepset.ai/cookbook/browser_agents) to better understand how the Agent works.

The Docker compose stack includes three containers:
- [Hayhooks](https://github.com/deepset-ai/hayhooks) - serves the Haystack Agent.
- [Playwright MCP server](https://github.com/microsoft/playwright-mcp) - handles browser automation.
- [Open WebUI](https://github.com/open-webui/open-webui) - provides the user interface.

**Repository Structure**
- `docker-compose.yml`: Docker compose configuration.
- `Dockerfile`: Dockerfile to build the Hayhooks container with additional dependencies (`mcp-haystack` and `google-genai-haystack`).
- `pipelines/browser_agent/pipeline_wrapper.py`: pipeline wrapper for the Browser Agent.


## ⚙️ Technical Details

### Hayhooks
- The current implementation **does not support multi-turn conversations**. Each message starts a new Agent task.

- The agent is exposed as a **REST API endpoint** via a Hayhooks pipeline wrapper. [Read more](https://github.com/deepset-ai/hayhooks?tab=readme-ov-file#deploy-an-agent).

- Streaming responses are suppored via Hayhooks's `async_streaming_generator`. [Read more](https://github.com/deepset-ai/hayhooks?tab=readme-ov-file#streaming-responses-in-openai-compatible-endpoints).

- Hayhooks sends events to Open WebUI to update the user interface in real time. [Read more](https://github.com/deepset-ai/hayhooks?tab=readme-ov-file#sending-open-webui-events-enhancing-the-user-experience).

### Docker Compose

- The Docker compose file is fully commented and ready for customization.

- Container dependencies:
    - The Hayhooks container requires the Playwright MCP server to be running and ready to accept requests via Streamable HTTP transport.

    - Similarly, Open WebUI depends on the Hayhooks container to be running.

    - These dependencies are managed using the `depends_on` directive in Docker Compose.

## 🔧 Customization

There are several things you can customize, and you can also take this repository as a starting point for deploying a Haystack Agent.


### Browser Agent

#### Tools
The Agent uses several Playwright MCP server tools:
- `browser_navigate`
- `browser_snapshot`
- `browser_click`
- `browser_type`
- `browser_navigate_back`
- `browser_wait_for`

⚠️ Tip: Only enable the tools you actually need to avoid confusing the LLM.

For more tools, see the [Playwright MCP server documentation](https://github.com/microsoft/playwright-mcp?tab=readme-ov-file#tools).

#### Models

- For browser automation tasks which generate long outputs, use models with **large context length**.

- Closed-source models generally work best, but open models with sufficient context length are also viable. Serving them on performant infrastructure or via providers (e.g., Groq) is recommended.

- Open models running on standard machines (e.g. via Ollama) usually reduce context length, limiting the Agent's effectiveness.

### Open WebUI
- The UI is highly configurable via **environment variables**. [Documentation](https://docs.openwebui.com/getting-started/env-configuration/)
- For production deployments, setup authentication. [Documentation](https://docs.openwebui.com/features/sso/)

### Running the Browser in headed mode

The demo focuses on Docker Compose deployment, so the headless browser in the MCP Docker container is the default and supported setup.

To experiment locally and see the **Agent interact with websites**, refer to [this notebook](https://haystack.deepset.ai/cookbook/browser_agents)
and replace the `server_info` definition as follows:

```python
server_info = StdioServerInfo(command="npx", args=["@playwright/mcp@latest"])
```

This lets you observe the Agent performing actions, for example navigating to Hugging Face Spaces and generating 
an image using an optimized prompt.

![Agent with Headed browser](headed_browser.gif)
