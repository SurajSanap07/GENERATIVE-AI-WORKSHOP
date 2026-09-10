%%writefile Multi-Agent-IT-Incident-Triager/README.md
# 🤖 Multi-Agent IT Incident Triager

A FastAPI-based multi-agent AI system that analyzes IT incident logs, identifies the root error, classifies incident severity, and recommends a resolution plan.

## 🚀 Project Overview

The Multi-Agent IT Incident Triager automates the initial analysis of IT support and production incidents.

Instead of manually reading large application logs, the system uses multiple AI agents:

1. **Extractor Agent** – Extracts the root error and affected service.
2. **Classifier Agent** – Determines the incident severity.
3. **Resolution Agent** – Generates a concise action plan.

The system exposes these capabilities through a REST API built with FastAPI.

## 🏗️ Architecture

```text
                 IT Incident Log
                        │
                        ▼
              ┌───────────────────┐
              │  FastAPI REST API  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Extractor Agent   │
              │ Root Error        │
              │ Affected Service  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Classifier Agent  │
              │ LOW / MEDIUM      │
              │ HIGH / CRITICAL   │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Resolution Agent  │
              │ 3-Step Action Plan│
              └─────────┬─────────┘
                        │
                        ▼
                 Incident Response