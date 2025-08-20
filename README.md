# MLOps Example

![Build Status](https://github.com/vasifvortex/azercell_project3/actions/workflows/ci-build.yaml/badge.svg)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![3.12](https://img.shields.io/badge/Python-3.12-green.svg)](https://shields.io/)

---

## Overview of the Project

This repository demonstrates how to build, dockerize, and deploy a machine learning application, RAG, with service communication, along with implementing CI/CD workflows using GitHub Actions and self-hosted runners.

## Architecture

- **Backend**: FastAPI for ML model serving and API endpoints
- **Frontend**: Streamlit for interactive web interface
- **Containerization**: Docker and Docker Compose for service orchestration
- **CI/CD**: GitHub Actions with self-hosted runner deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Running the Application

1. **Clone the repository**
   ```bash
   git clone https://github.com/vasifvortex/azercell_project3.git
   cd azercell_project3
   ```

2. **Launch services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend (Streamlit): `http://localhost:8501`
   - Backend API (FastAPI): `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

4. **Stop the application**
   ```bash
   docker-compose down
   ```

## Project Structure

```
azercell_project3/
├── backend/              # FastAPI application
├── frontend/             # Streamlit application
├── docker-compose.yml    # Service orchestration
├── .github/workflows/    # CI/CD pipelines
└── README.md
```

## Development Setup

### For Server Deployment (Ubuntu)

1. **Add user to docker group** (to run docker commands without sudo)
   ```bash
   sudo usermod -aG docker ubuntu
   ```

2. **Create GitHub self-hosted runner**
   - Go to your repository **Settings** → **Actions** → **Runners**
   - Click **"New self-hosted runner"** and select **Linux**
   - Follow all the setup steps provided by GitHub **except the last step**
   - Don't run `./run.sh` directly as shown in GitHub instructions

3. **Launch GitHub runner in detached mode**
   ```bash
   nohup ./run.sh > runner.log 2>&1 &
   ```

## Key Features

- **Dockerized Services**: Both backend and frontend are containerized for consistent deployment
- **Service Communication**: Demonstrates proper inter-service communication patterns
- **CI/CD Pipeline**: Automated testing and deployment using GitHub Actions
- **Self-hosted Runner**: Shows how to set up and use self-hosted runners for deployment
- **Learning Playground**: Intended for exploring and practicing MLOps concepts

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://opensource.org/licenses/Apache-2.0) file for details.

