# Browser Agent

This demo shows how to deploy a Browser Agent with [Docker Compose](https://docs.docker.com/compose/).

Here you can see it in action, while it finds public transportation travel options from Paris to Berlin.

![Browser Agent](video.gif)


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
Open your browser to [http://localhost:3000/](http://localhost:3000/) and start talking with the Agent.



## 📖 Overview
The Agent is built with Haystack, Google Gemini 2.5 Flash model, and the Playwright MCP server for browser automation.
Take a look at [this notebook](https://haystack.deepset.ai/cookbook/browser_agents) to better understand how the Agent works.

The Docker compose stack includes three containers:
- [Hayhooks](https://github.com/deepset-ai/hayhooks) to serve the Haystack Agent
- [Playwright MCP server](https://github.com/microsoft/playwright-mcp) for browser automation
- [Open WebUI](https://github.com/open-webui/open-webui) for the user interface.

Repository Structure
- `docker-compose.yml`: Docker compose file to run the containers.
- `Dockerfile`: Dockerfile to build the Hayhooks container with additional dependencies (`mcp-haystack` and `google-genai-haystack`).
- `pipelines/browser_agent/pipeline_wrapper.py`: the pipeline wrapper for the Browser Agent.


## Technical Details

### Hayhooks
- The current implementation is not built for multi-turn conversations, so with each message you'll give a new task
  to the Agent, restarting from scratch.

- The agent is exposed as a REST API endpoint, by defining a Hayhooks pipeline wrapper. Read about it in [Hayhooks README](https://github.com/deepset-ai/hayhooks?tab=readme-ov-file#deploy-an-agent).

- The pipeline Wrapper for the Agent uses an `async_streaming_generator` to stream OpenAI-compatible outputs as soon as
they are generated. Read about it in [Hayhooks README](https://github.com/deepset-ai/hayhooks?tab=readme-ov-file#streaming-responses-in-openai-compatible-endpoints).

- The pipeline wrapper sends events to Open WebUI to update the user interface and improve the user experience. Read about it in [Hayhooks README](https://github.com/deepset-ai/hayhooks?tab=readme-ov-file#sending-open-webui-events-enhancing-the-user-experience).

### Docker Compose

The Docker compose file is fully commented and ready for customization.

The Hayhooks container need the Playwright MCP server to be running and ready to accept requests via Streamable HTTP transport; similarly, Open WebUI needs the Hayhooks container to be ready to accept requests from Open WebUI. This is done by using the `depends_on` directive in the Docker compose file.

## 🔧 Customization

There are several things you can customize and you can also take this repo as a starting point for deploying an Agent.


### Browser Agent

#### Tools
The Agent uses several tools from Playwright MCP server:
- `browser_navigate`
- `browser_snapshot`
- `browser_click`
- `browser_type`
- `browser_navigate_back`
- `browser_wait_for`

When working with tools for LLMs, it's a good practice to only select the ones you actually need. This helps avoid confusing the LLM with too many options.

In case you need different or more tools, read the [Playwright MCP server documentation](https://github.com/microsoft/playwright-mcp?tab=readme-ov-file#tools) to discover all the available tools.

#### Models
Most recent closed models with a large context length should work well. I have tried
some of them.
The browser automation tool returns very long responses, so the context length is an important requirement.

Also recent open models with a large context length should work. The best idea is to serve them in a performant infrastucture
or via providers like Groq. When you try using open models running on a standard machine (e.g. via Ollama), the problem is that the context length is
reduced and the Agent is not able to respond in a meaningful way.

### Open WebUI
The user interface is highly customizable and you can do a lot of things using environment variables.
Read more about it in the [Open WebUI documentation](https://docs.openwebui.com/getting-started/env-configuration/).

Of course, if you deploy the Agent in the real world, you will have to setup an authentication mechanism.
Read more about it in the [Open WebUI documentation](https://docs.openwebui.com/features/sso/).

