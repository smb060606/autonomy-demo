# Fact-Check News - AI-Powered News Verification System

An Autonomy application that enables news editors to fact-check articles using parallel AI agents and web search.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Web UI (Next.js)                            │
│                     ┌──────────────────────┐                        │
│                     │  Article Input Box   │                        │
│                     └──────────┬───────────┘                        │
│                                │                                     │
│                                ▼                                     │
│                     ┌──────────────────────┐                        │
│                     │  Fact-Check Report   │                        │
│                     └──────────────────────┘                        │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTP API
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Autonomy Backend                                │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │                    Orchestrator Agent                      │    │
│  │  - Receives article text                                   │    │
│  │  - Coordinates workflow                                    │    │
│  │  - Returns final report                                    │    │
│  └──────────────────┬──────────────────────┬──────────────────┘    │
│                     │                      │                        │
│                     ▼                      ▼                        │
│  ┌─────────────────────────┐   ┌────────────────────────┐         │
│  │  Claim Extraction Agent │   │ Report Generation Agent│         │
│  │  - Parses article       │   │ - Compiles all findings│         │
│  │  - Identifies claims    │   │ - Creates final report │         │
│  │  - Returns claim list   │   │ - Formats for display  │         │
│  └────────────┬────────────┘   └───────────▲────────────┘         │
│               │                             │                       │
│               │ Claims                      │ Research Results      │
│               ▼                             │                       │
│  ┌────────────────────────────────────────────────────────┐        │
│  │         Parallel Fact-Checking Agents                  │        │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │        │
│  │  │ Agent 1  │  │ Agent 2  │  │ Agent N  │ ...        │        │
│  │  │ Claim 1  │  │ Claim 2  │  │ Claim N  │            │        │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘            │        │
│  │       │             │             │                    │        │
│  └───────┼─────────────┼─────────────┼────────────────────┘        │
│          │             │             │                              │
│          └─────────────┴─────────────┘                              │
│                        │                                            │
│                        ▼                                            │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │           Brave Search MCP Server                       │       │
│  │  - Web search capability                                │       │
│  │  - Returns search results                               │       │
│  │  - Provides evidence sources                            │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Workflow

1. **Editor Input**: Editor pastes news article into the web UI text box
2. **Claim Extraction**: Orchestrator sends article to Claim Extraction Agent
   - Analyzes article structure
   - Identifies factual claims that can be verified
   - Returns structured list of claims
3. **Parallel Fact-Checking**: Each claim assigned to a dedicated agent
   - Agents run in parallel for maximum speed
   - Each agent uses Brave Search MCP to research their claim
   - Agents gather evidence and determine claim veracity
4. **Report Generation**: All research compiled into final report
   - Report Generation Agent receives all fact-check results
   - Creates comprehensive, well-formatted report
   - Includes claim-by-claim analysis with sources
5. **Display Results**: Report shown in web UI
   - Clear visualization of verified/disputed claims
   - Source links for transparency
   - Overall article assessment

## Technology Stack

- **Autonomy Computer**: Agent orchestration and deployment platform
- **Python**: Backend agent logic and FastAPI server
- **Brave Search MCP**: Web search capability via Model Context Protocol
- **Next.js**: Modern React framework for web UI
- **shadcn/ui**: Beautiful, accessible UI components
- **Claude Sonnet 4**: LLM powering the intelligent agents

## Project Structure

```
autonomy-demo/
├── README.md                    # This file
├── autonomy.yaml                # Autonomy deployment configuration
├── secrets.yaml                 # API keys (not committed to git)
├── .gitignore                   # Excludes secrets from version control
├── images/
│   └── main/
│       ├── Dockerfile           # Container definition
│       ├── main.py              # Python backend with agents
│       └── public/              # Compiled Next.js static files
└── ui/
    ├── package.json             # UI dependencies
    ├── next.config.js           # Next.js configuration
    ├── tsconfig.json            # TypeScript configuration
    ├── components.json          # shadcn/ui configuration
    ├── tailwind.config.js       # Tailwind CSS configuration
    ├── app/
    │   ├── layout.tsx           # Root layout
    │   └── page.tsx             # Main fact-check interface
    └── components/
        └── ui/                  # shadcn/ui components
```

## Prerequisites

1. **Autonomy Account**: Sign up at https://my.autonomy.computer
2. **Autonomy CLI**: Install with `curl -sSfL autonomy.computer/install | bash`
3. **Docker**: Install from https://www.docker.com/get-started/
4. **Brave Search API Key**: Get from https://brave.com/search/api/
5. **Node.js**: Version 18+ for Next.js development

## Setup Instructions

### 1. Configure Brave Search API

Create `secrets.yaml` with your Brave Search API key:

```yaml
BRAVE_API_KEY: "your_brave_api_key_here"
```

**Important**: This file is excluded from git via `.gitignore`

### 2. Build the UI

```bash
cd ui
npm install
npm run build-autonomy
cd ..
```

This compiles the Next.js app and copies static files to `images/main/public/`

### 3. Enroll with Autonomy

```bash
autonomy cluster enroll --no-input
```

Follow the browser prompt to authenticate.

### 4. Deploy the Application

```bash
autonomy zone deploy
```

Note the cluster and zone names from the output.

### 5. Access Your App

Once deployed, your app will be available at:

```
https://${CLUSTER}-${ZONE}.cluster.autonomy.computer/
```

Replace `${CLUSTER}` and `${ZONE}` with your actual values.

## API Endpoints

### POST `/api/fact-check`

Submit an article for fact-checking.

**Request:**
```json
{
  "article": "Full article text to fact-check..."
}
```

**Response:**
```json
{
  "report": "Detailed fact-check report with claim analysis...",
  "status": "completed"
}
```

### GET `/agents`

List all running agents.

## Development

### Run UI Locally

```bash
cd ui
npm run dev
```

Visit http://localhost:3000 (note: will not connect to backend unless deployed)

### View Logs

```bash
autonomy zone inlet --to logs > logs_server.log 2>&1 &
LOGS_PID=$!
sleep 3
LOGS_PORT=$(grep -o "localhost:[0-9]*" logs_server.log | cut -d: -f2 | head -1)
open "http://127.0.0.1:$LOGS_PORT"
```

### Redeploy After Changes

```bash
# Rebuild UI if changed
cd ui && npm run build-autonomy && cd ..

# Deploy updated zone
autonomy zone deploy
```

## How It Works

### Claim Extraction Agent

Uses Claude Sonnet 4 to intelligently parse articles and identify specific factual claims. Outputs structured JSON with:
- Claim text
- Claim type (statistic, quote, event, etc.)
- Context from article

### Fact-Checking Agents

Each claim gets a dedicated agent that:
1. Formulates search queries
2. Uses Brave Search MCP to find sources
3. Analyzes evidence credibility
4. Determines claim veracity (True/False/Partially True/Unverifiable)
5. Provides sources and reasoning

### Report Generation Agent

Synthesizes all fact-check results into a cohesive report:
- Executive summary
- Claim-by-claim breakdown
- Source citations
- Overall article credibility assessment

## Performance

- **Parallel Processing**: Multiple claims checked simultaneously
- **Scalability**: Thousands of agents can run concurrently
- **Speed**: Typical article (5-10 claims) fact-checked in 30-60 seconds

## Security

- API keys stored in `secrets.yaml` (not committed)
- Environment variables injected at runtime
- Secure MCP connections within Autonomy cluster

## License

MIT

## Support

For issues with:
- **Autonomy Platform**: Join Discord at https://autonomy.computer/docs/start/discord.md
- **This Application**: Open an issue in this repository
