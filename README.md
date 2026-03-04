# Clara Answers - AI Agent Onboarding Automation Pipeline

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-required-inactive.svg)](https://www.docker.com/)
[![n8n](https://img.shields.io/badge/n8n-orchestration-red.svg)](https://n8n.io/)

## What This Project Does

This project automates the transformation of unstructured call transcripts into production-ready AI voice agent configurations. 

**The Challenge:**
Converting messy, real-world conversation data into structured operational rules that power intelligent voice agents.

**The Solution:**
A fully automated pipeline that processes demo and onboarding call transcripts, extracts operational constraints using a local LLM, generates agent specifications, and tracks all changes with detailed version control.

## Table of Contents

- [Project Overview](#project-overview)
- [How It Works](#how-it-works)
- [Data Flow](#data-flow)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Usage](#usage)
- [Input Format](#input-format)
- [Output Files](#output-files)
- [Features](#features)
- [Troubleshooting](#troubleshooting)

## Project Overview

This assignment was created for the ZenTrades AI hiring process and demonstrates automated agent onboarding at scale. It simulates Clara's real-world challenge of converting human conversations into deployable AI voice agent configurations.

**Key Capabilities:**
- ✅ Automatic data extraction from transcripts using Ollama (Llama 3.2)
- ✅ Two-stage pipeline: Demo (v1) → Onboarding (v2)
- ✅ Change tracking and versioning with detailed changelogs
- ✅ Interactive HTML dashboard with batch metrics
- ✅ Asana task integration for team collaboration
- ✅ Comprehensive error handling and logging
- ✅ Zero-cost LLM inference using local Ollama

## How It Works

### Stage 1: Demo Call Processing (Pipeline v1)

1. **Input**: Demo transcript (e.g., `account_1_demo.txt`)
2. **Extraction**: LLM extracts initial operational assumptions
3. **Output**: 
   - `memo.json` - Preliminary operational rules
   - `agent_spec.json` - Initial Retell AI agent configuration
4. **Tracking**: Asana task created for v1 completion

### Stage 2: Onboarding Call Processing (Pipeline v2)

1. **Input**: Onboarding transcript (e.g., `account_1_onboarding.txt`)
2. **Extraction**: LLM extracts finalized operational constraints
3. **Merging**: Compares and merges v1 with v2 data
4. **Output**:
   - `memo.json` (v2) - Updated operational rules
   - `agent_spec.json` (v2) - Production-ready agent configuration
5. **Changelog**: Documents all changes between v1 and v2
6. **Tracking**: Asana tasks created for v2 completion and changelog

### Stage 3: Dashboard Generation

- Compiles results from all processed accounts
- Generates interactive HTML dashboard
- Provides batch metrics and visual diff viewer

## Data Flow

```
Demo Transcript
    ↓
[Ollama LLM Extraction]
    ↓
memo.json (v1) + agent_spec.json (v1)
    ↓
         ↓ (Asana Task Created)
         ↓
Onboarding Transcript
    ↓
[Ollama LLM Extraction]
    ↓
memo.json (v2) + [Data Merge]
    ↓
memo.json (final) + agent_spec.json (v2) + changes.json + changes.md
    ↓
[Dashboard Generation]
    ↓
dashboard.html (with metrics & diffs)
```

## Repository Structure

```
clara-answers-assignment/
├── inputs/                          # Input transcript files
│   ├── account_1_demo.txt
│   ├── account_1_onboarding.txt
│   ├── account_2_demo.txt
│   ├── account_2_onboarding.txt
│   └── ...
│
├── outputs/                         # Generated outputs
│   ├── dashboard.html              # Interactive summary dashboard
│   └── accounts/                   # Per-account results
│       ├── account_1/
│       │   ├── v1/
│       │   │   ├── agent_spec.json
│       │   │   └── memo.json
│       │   └── v2/
│       │       ├── agent_spec.json
│       │       └── memo.json
│       ├── account_2/
│       │   └── ...
│       └── ...
│
├── changelog/                       # Version history
│   ├── account_1/
│   │   ├── changes.json           # Structured v1→v2 changes
│   │   └── changes.md             # Human-readable changelog
│   ├── account_2/
│   │   └── ...
│   └── ...
│
├── scripts/                         # Python processing scripts
│   ├── pipeline_v1.py              # Demo processing → v1
│   ├── pipeline_v2.py              # Onboarding → v2 merge
│   ├── extract_v1.py               # Legacy: direct extraction
│   ├── extract_v2.py               # Legacy: direct extraction
│   ├── diff_v1_v2.py               # Legacy: diff generation
│   └── generate_dashboard.py       # Dashboard HTML creation
│
├── workflows/                       # n8n workflow definitions
│   └── My workflow.json            # Complete orchestration workflow
│
├── temp/                           # Temporary processing files
├── docker-compose.yml              # Docker services configuration
├── Dockerfile                      # Custom image (Node + Python)
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## Prerequisites

- **Docker & Docker Compose** (latest version)
- **Git** for cloning the repository
- **Web browser** for n8n UI (localhost:5678) and dashboard view
- **Asana Account** with API token (free tier available - see below)
- **4GB+ RAM** recommended for comfortable Ollama operation

**What Gets Installed Automatically:**
- Node.js 20 (via Docker)
- Python 3 (via Docker)
- Ollama with Llama 3.2 model
- n8n (open-source workflow automation)

### Getting Your Asana API Token

Asana provides a **free tier with unlimited task creation**, which is perfect for this assignment that uses only free tools.

**Steps to get your Asana API token:**

1. **Create a free Asana account** (if you don't have one):
   - Go to https://asana.com
   - Sign up with your email (free tier offers plenty of functionality)

2. **Generate an API token**:
   - In Asana, go to **Settings** → **Apps** → **Personal Access Tokens**
   - Click **Create new token**
   - Name it something like "Clara Pipeline"
   - Copy the generated token (save it somewhere safe)
   - **⚠️ Important:** You'll only see this token once, so copy it immediately

3. **Keep your token ready** for n8n configuration in Step 4 of the Detailed Setup

## Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd clara-answers-assignment

# 2. Start all services (build and run in background)
docker compose up --build -d

# 3. Wait 30-60 seconds for services to initialize
# Then open n8n in your browser
http://localhost:5678

# 4. In n8n:
#    - Create a new workflow
#    - Import: workflows/My workflow.json
#    - Click "Execute Workflow"

# 5. View results
#    Open: outputs/dashboard.html in your browser
```

## Detailed Setup

### Step 1: Clone and Enter Directory

```bash
git clone https://github.com/yourusername/clara-answers-assignment.git
cd clara-answers-assignment
```

### Step 2: Build and Start Services

```bash
# Build Docker image and start all services in background
docker compose up --build -d

# Verify services are running
docker ps

# Expected output should show containers for:
# - n8n (port 5678)
# - Ollama (port 11434)
```

### Step 3: Prepare Input Files

Place transcript files in the `inputs/` directory following this naming convention:

```
inputs/
├── account_1_demo.txt          # Required: Demo transcript
├── account_1_onboarding.txt    # Required: Onboarding transcript
├── account_2_demo.txt
├── account_2_onboarding.txt
└── ...
```

**Important:** File names MUST follow the pattern `account_X_demo.txt` and `account_X_onboarding.txt` where X is an account number.

### Step 4: Import Workflow into n8n

1. Open http://localhost:5678 in your browser
2. Sign up / log in (initial credentials can be anything)
3. Click **New** to create a new workflow
4. Look for the **Import** button in the top menu
5. Select `workflows/My workflow.json`
6. Click **Save workflow**

### Step 5: Configure Asana Credentials in n8n

The workflow contains 3 Asana nodes. You'll configure credentials on one of them, and it will be available to all:

1. In the imported workflow, click on any of the **Asana nodes** (you'll see them labeled in the workflow)
2. In the right panel, find the **Credential** section
3. Click the dropdown next to "Asana API" to create a new credential
4. In the credential dialog that appears, paste your Asana API token in the **Token** field
5. Click **Save** and then **Close**

### Step 6: Execute the Workflow

1. Click **Execute Workflow** button
2. Monitor execution in the n8n UI
3. Check console for any errors
4. Workflow will process ALL files in `inputs/` folder
5. Check your Asana workspace to see the automatically created tasks

### Step 7: View Results

- **Dashboard**: Open `outputs/dashboard.html` in your browser
- **Agent Specs**: Found in `outputs/accounts/account_X/v1/` and `v2/`
- **Changelogs**: Found in `changelog/account_X/`

## Usage

### Running the Workflow

```bash
# Services must be running (from docker compose up)
# Then simply:
# 1. Open http://localhost:5678
# 2. Import the workflow
# 3. Click "Execute Workflow"
```

### Processing Custom Data

To process your own transcripts:

1. **Add files to `inputs/` folder**:
   ```
   inputs/
   ├── account_6_demo.txt        # Your demo call transcript
   └── account_6_onboarding.txt  # Your onboarding call transcript
   ```

2. **Execute workflow** - it will automatically process new files

3. **Results appear in**:
   - `outputs/accounts/account_6/v1/` (demo results)
   - `outputs/accounts/account_6/v2/` (onboarding results)
   - `changelog/account_6/` (changes)

### Re-running the Workflow

To re-run on existing data:
- Simply execute the workflow again - outputs are overwritten
- Previous json and markdown files are replaced

## Input Format

### Demo Transcript Format

**File**: `account_X_demo.txt`

A natural conversation between client and sales representative discussing initial requirements.

**Example** (`account_1_demo.txt`):
```
Client: Hi, I run Frosty Air HVAC. We need an AI to answer calls. 
We do AC and heating. Emergencies are mostly total AC failure in the summer 
or furnace failure in winter. We're open 8 to 5 usually. If someone calls 
after hours with an emergency, I want the AI to send it to the on-call guy. 
For normal stuff, just take a message.
```

### Onboarding Transcript Format

**File**: `account_X_onboarding.txt`

A detailed conversation confirming exact operational parameters discovered during onboarding.

**Example** (`account_1_onboarding.txt`):
```
Developer: Let's finalize the setup for Frosty Air HVAC.
Client: Our exact hours are Monday through Friday, 8:00 AM to 6:00 PM 
Central Time. For emergencies—which we strictly define as total system 
failure in extreme weather or gas leaks—transfer the call to 555-0101. 
For non-emergencies after hours, just take their name and number and 
we'll call them the next morning. One strict rule: never book commercial 
jobs through the AI, those must be handled by our sales team.
```

## Output Files

### memo.json

Structured operational parameters extracted from transcripts:

```json
{
  "account_id": "account_1",
  "company_name": "Frosty Air HVAC",
  "business_hours": {
    "days": "Monday-Friday",
    "start": "08:00",
    "end": "18:00",
    "timezone": "Central"
  },
  "emergency_definition": [
    "Total AC failure in summer",
    "Furnace failure in winter",
    "Gas leaks"
  ],
  "emergency_routing_rules": "Transfer to 555-0101",
  "integration_constraints": [
    "Never book commercial jobs through AI"
  ],
  "questions_or_unknowns": []
}
```

### agent_spec.json

Production-ready Retell AI voice agent configuration.

```json
{
  "agent_name": "Frosty Air HVAC Clara Assistant",
  "channel": "voice",
  "language": "en-US",
  "retellLlmData": {
    "general_prompt": "You are Clara, the automated assistant for Frosty Air HVAC...",
    "general_tools": [
      {
        "type": "transfer_call",
        "name": "transfer_call",
        "transfer_destination": {
          "type": "predefined",
          "number": "555-0101"
        }
      }
    ]
  }
}
```

### changes.json

Structured record of all changes between v1 and v2:

```json
[
  {
    "file": "memo.json",
    "field": "business_hours",
    "old_value": { "days": "", "start": "", "end": "", "timezone": "" },
    "new_value": { "days": "Mon-Fri", "start": "08:00", "end": "18:00", "timezone": "Central" },
    "reason": "Confirmed exact hours during onboarding call"
  }
]
```

### changes.md

Human-readable markdown changelog for documentation:

```markdown
# Changelog for account_1

- **[memo.json] business_hours**: `{}` → `{"days":"Mon-Fri",...}`
  - *Reason*: Confirmed exact hours during onboarding call

- **[memo.json] emergency_definition**: `[]` → `["Total AC failure","Gas leaks"]`
  - *Reason*: Clarified emergency scenarios during onboarding
```

### dashboard.html

Interactive web dashboard with:
- Total accounts processed
- v1 and v2 completion metrics
- Visual diff viewer for all changes
- Overall summary statistics

## Features

### Automated Extraction
- Uses Ollama + Llama 3.2 for zero-cost LLM inference
- Extracts structured JSON from unstructured transcripts
- Strict schema validation

### Two-Stage Processing
- **Stage 1 (v1)**: Initial assumptions from demo calls
- **Stage 2 (v2)**: Finalized rules from onboarding calls
- Intelligent merging preserves context

### Change Tracking
- Field-level diff tracking
- Changelog in JSON and Markdown formats
- Reason documentation for each change

### Team Integration
- **Asana Task Tracking**:
  - Automatic task creation for v1 completion
  - Automatic task creation for v2 completion
  - Automatic task creation for changelog generation
  - Error tasks for pipeline failures

### Error Handling
- Graceful failure handling with error tasks
- Detailed error logging in Asana
- Pipeline continues on script failures

### Dashboard & Reporting
- Interactive HTML dashboard
- Batch metrics and status overview
- Visual diff viewer for all changes

## Troubleshooting

### Common Issues

**Issue**: LLM output is inconsistent
- This is expected behavior with Llama 3.2
- Increase temperature/sampling parameters in pipeline scripts if needed

### Checking Logs

```bash
# Check if files are being created
ls -la outputs/accounts/
ls -la changelog/
```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (careful - deletes outputs)
docker compose down -v

# Restart services
docker compose up -d
```

## Architecture Details

### Technology Stack
- **Orchestration**: n8n (low-code workflow automation)
- **LLM Provider**: Ollama (local, zero-cost inference)
- **Model**: Llama 3.2 (7B parameters)
- **Processing**: Python 3 (data extraction, merging, formatting)
- **Container**: Docker + Docker Compose
- **Integration**: Asana API (task tracking)

### Docker Images
- **n8n**: Node.js 20 on bookworm-slim
- **Custom**: Node 20 + Python 3 (for running scripts)
- **Ollama**: Official Ollama image with Llama 3.2

## License

This project is licensed under the MIT License.

---

**Built for**: ZenTrades AI Hiring Process  
**Project Purpose**: Automating Agent Onboarding at Scale