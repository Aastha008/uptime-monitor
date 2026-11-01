# Uptime Monitor

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Framework](https://img.shields.io/badge/framework-FastAPI-009688.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> A lightweight, self-hosted service health and uptime tracking application featuring real-time state transition alerts, non-blocking asynchronous probing, and an integrated analytical dashboard.

---

## Overview & Problem Statement

Modern engineering teams often manage a sprawling array of microservices, internal tools, and private APIs. Relying on commercial third-party SaaS monitoring services introduces several critical operational drawbacks:

* **High Cost & Scale Limits:** Tiered pricing models scale aggressively as endpoint count and check frequencies increase.
* **Security & Privacy Risks:** Internal microservices and private VPC endpoints cannot be monitored without exposing endpoints to the public internet or managing complex VPN tunnels.
* **Vendor Lock-in:** Custom metric aggregation and tailored incident workflows are often restricted by SaaS provider features.

**Uptime Monitor** solves these challenges by providing a zero-external-dependency, self-hosted service health engine. Operating entirely inside your network, it periodically executes non-blocking HTTP and TCP health probes, persists low-overhead telemetry to an SQLite database, generates latency trend visualisations, and immediately dispatches alerts when endpoints transition between healthy, degraded, or down states.

---

## Key Features

* **Flexible Endpoint Management:** Configure target HTTP/TCP URLs, customized polling intervals, expected HTTP success codes, and strict connection/response timeout thresholds via REST endpoints or the web dashboard.
* **Asynchronous Probing Engine:** High-throughput, non-blocking background polling worker powered by `HTTPX` and `asyncio` capable of monitoring hundreds of concurrent endpoints with minimal CPU and memory overhead.
* **Interactive Visual Dashboard:** Embedded Jinja2 & HTML5 frontend enhanced with Chart.js to render 24-hour and 30-day uptime percentages, real-time latency sparklines, and detailed historical incident logs.
* **State-Driven Webhook Dispatcher:** Outbound alert engine that tracks state changes (`HEALTHY` $\leftrightarrow$ `DEGRADED` $\leftrightarrow$ `DOWN`) and fires structured JSON webhooks to custom notification destinations (e.g., Slack, Discord, internal webhooks).

---

## System Architecture

Uptime Monitor is built on an asynchronous event loop that cleanly decouples background telemetry collection from client-facing API requests and frontend rendering.

```
                  +-----------------------------------+
                  |   Browser / Dashboard User UI     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |        FastAPI Router Engine      |
                  |     (src/api.py & src/main.py)    |
                  +-----------------------------------+
                    /               |               \
                   /                v                \
      +-------------------+  +--------------+  +-------------------+
      | Jinja2 Dashboard  |  | Pydantic/ORM |  | Core Health Engine|
      |   (HTML / JS)     |  | (models.py)  |  |   (src/core.py)   |
      +-------------------+  +--------------+  +-------------------+
                                    |                    ^
                                    v                    |
                             +--------------+   +------------------+
                             |  SQLite DB   |   | Async Worker     |
                             |  (src/db.py) |<--| (src/worker.py)  |
                             +--------------+   +------------------+
                                                         |
                                                         v
                                                +------------------+
                                                | Webhook Alerts   |
                                                | (src/alerts.py)  |
                                                +------------------+
```

### Module Responsibilities

* **`src/db.py`**: Configures the async SQLAlchemy engine (`sqlite+aiosqlite`), handles session lifecycles, and executes initial schema migrations.
* **`src/models.py`**: Defines SQLAlchemy ORM database entities and Pydantic schemas for endpoints, execution check logs, historical incidents, and webhook alert configurations.
* **`src/core.py`**: Contains core probe logic (HTTP status check, response time measurement, TCP port ping) and mathematical formulas for computing windowed uptime percentages.
* **`src/alerts.py`**: Tracks continuous state transitions for monitored targets and dispatches formatted webhook notifications.
* **`src/worker.py`**: Manages the persistent background task loop, scheduling probe executions based on each target's configured check interval.
* **`src/api.py`**: Implements REST API endpoints for CRUD management of endpoints, JSON metrics querying, and HTML dashboard rendering using Jinja2 templates.
* **`src/main.py`**: Application bootstrap script that initialises FastAPI, handles startup/shutdown lifecycles for the background worker, and serves the application.

---

## Technology Stack

* **Language:** Python 3.11+
* **Framework:** FastAPI
* **Database & ORM:** SQLite, SQLAlchemy (Async extension), Pydantic v2
* **HTTP & Async I/O:** HTTPX, asyncio, aiosqlite
* **Templating & Visualisation:** Jinja2, HTML5, Chart.js
* **Testing & Quality:** pytest, pytest-asyncio, HTTPX TestClient

---

## Installation & Setup

### Prerequisites

Ensure you have Python 3.11 or higher installed on your machine.

### Setup Virtual Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/uptime-monitor.git
   cd uptime-monitor
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   * **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```
   * **Windows:**
     ```cmd
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Environment Variables Configuration

The application reads configuration values from standard environment variables or a `.env` file located in the project root.

Copy the template file to begin:
```bash
cp .env.example .env
```

### Configuration Options

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./uptime_monitor.db` | Async SQLAlchemy database connection string |
| `HOST` | `127.0.0.1` | Network interface address to bind the web server |
| `PORT` | `8000` | Port number on which the web application listens |
| `POLL_INTERVAL_DEFAULT` | `60` | Default fallback probe interval in seconds |
| `WEBHOOK_TIMEOUT` | `5.0` | Timeout in seconds for outbound notification webhooks |
| `LOG_LEVEL` | `INFO` | System logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Usage Guide

### Starting the Server

Run the application directly using Python or `uvicorn`:

```bash
python -m src.main
```

Alternatively, launch using Uvicorn directly for hot-reloading during development:

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

Once running, access the dashboard by navigating to `http://127.0.0.1:8000` in your browser.

---

### REST API Reference

Uptime Monitor provides a programmatic REST API for endpoint integration and metric extraction.

#### 1. Register a Monitored Endpoint

* **`POST /api/v1/endpoints`**

**Request Body:**
```json
{
  "name": "Payment Gateway API",
  "url": "https://api.payments.internal/health",
  "check_interval_seconds": 30,
  "expected_status_code": 200,
  "timeout_seconds": 3.0,
  "webhook_url": "https://hooks.slack.com/services/T00/B00/X00"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Payment Gateway API",
  "url": "https://api.payments.internal/health",
  "check_interval_seconds": 30,
  "expected_status_code": 200,
  "timeout_seconds": 3.0,
  "webhook_url": "https://hooks.slack.com/services/T00/B00/X00",
  "status": "HEALTHY",
  "created_at": "2026-03-30T10:00:00Z"
}
```

#### 2. Retrieve All Endpoints & Metrics

* **`GET /api/v1/endpoints`**

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Payment Gateway API",
    "url": "https://api.payments.internal/health",
    "status": "HEALTHY",
    "uptime_24h": 99.95,
    "uptime_30d": 99.80,
    "avg_latency_ms": 142.5
  }
]
```

#### 3. Fetch Incident Log

* **`GET /api/v1/incidents`**

**Response (200 OK):**
```json
[
  {
    "id": 42,
    "endpoint_id": 1,
    "started_at": "2026-03-30T08:14:00Z",
    "resolved_at": "2026-03-30T08:17:30Z",
    "cause": "HTTP status code 503 Service Unavailable (Expected 200)"
  }
]
```

---

## Automated Testing

The repository includes suite testing covering health check core routines and FastAPI endpoint routing using `pytest`.

### Execute Test Suite

Run all tests:
```bash
pytest
```

Run tests with detailed execution output:
```bash
pytest -v
```

Generate a code coverage report:
```bash
pytest --cov=src --cov-report=term-missing
```

---

## Project Structure

```
uptime-monitor/
│
├── .env.example            # Template for environment configuration
├── .gitignore              # Ignored files and directory rules
├── requirements.txt        # Production and development dependencies
│
├── src/                    # Primary application package
│   ├── __init__.py         # Package initialization marker
│   ├── main.py             # App bootstrap, lifecycle & server startup
│   ├── api.py              # FastAPI endpoints & dashboard router
│   ├── core.py             # Probe execution & latency/uptime calculations
│   ├── db.py               # Async SQLAlchemy setup & connection management
│   ├── models.py           # ORM models and Pydantic validation schemas
│   ├── alerts.py           # State management & webhook notifications
│   └── worker.py           # Async background task execution loop
│
└── tests/                  # Automated test suite
    ├── __init__.py         # Test package initialization
    ├── test_api.py         # REST API endpoint test cases
    └── test_core.py        # Probe engine and logic test cases
```

---

## Roadmap & Future Enhancements

* [ ] **Prometheus Metrics Exporter:** Expose a `/metrics` scrapable endpoint for native integration with Grafana.
* [ ] **Multi-Region Probing:** Support distributed agent nodes for remote health checks across global locations.
* [ ] **Multi-channel Alerting:** Expand beyond generic webhooks to natively support PagerDuty, Telegram, Email (SMTP), and Twilio SMS.
* [ ] **TLS Cert Expiry Monitoring:** Compute and alert on SSL/TLS certificate validity windows.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.