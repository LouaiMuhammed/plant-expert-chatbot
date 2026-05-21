# Plant Expert Chatbot
## RAG-Based Chatbot For "Thamara" App


### Requirements

- Python **3.10.11**


### Reproducing the Project

1. Clone the repository

```bash
git clone <your-repo-url>
cd plant-disease-detection-using-cnns
```

2. Create and activate a virtual environment



```bash
- Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

- Linux / macOS

python -m venv .venv
source .venv/bin/activate
```
## Installation
### Required Packages
```bash
$ pip install requirements.txt
```
### Environment Variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file.

## Docker

This project should be run with the modern Docker Compose CLI:

```bash
docker compose -f docker/docker_compose.yml up -d
```

Notes:

- `docker-compose` may not exist on newer Docker Desktop installs. Use `docker compose` instead.
- The compose file lives at `docker/docker_compose.yml`, so `-f` is required.
- If `docker` is not recognized, install Docker Desktop and reopen your terminal so `docker` is added to `PATH`.
