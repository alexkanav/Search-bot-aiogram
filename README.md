# Marketplace Search Bot

A microservices-based Telegram bot for searching marketplace listings based on user-defined criteria, with **continuous monitoring**, **database-backed item history**, and **asynchronous communication between microservices**.

The system consists of two independent services: the **Telegram Bot** and the **Marketplace Search Service**, which communicate primarily through **RabbitMQ**.

---

## Features

- Search marketplace listings by query and price
- Select marketplace regions and locations
- One-time or continuous searches
- Periodic monitoring for new listings
- Instant Telegram notifications
- Support for multiple marketplaces
- Store found items in MongoDB
- Automatic expiration of stored marketplace items
- Redis-based FSM storage and caching
- Asynchronous communication through RabbitMQ
- Service-to-service authentication
- Playwright-based scraping
- Unit and integration testing with pytest

---

## Tech Stack

- **Python 3.12+**
- **Aiogram 3** — Telegram bot framework
- **FastAPI** — Marketplace Search Service API
- **Playwright** — Marketplace scraping
- **RabbitMQ** — Asynchronous inter-service communication
- **MongoDB** — Marketplace item storage
- **Redis** — FSM storage and caching
- **Pydantic Settings** — Configuration management
- **Docker** — Containerization
- **Pytest** — Testing

---

## Architecture

The application is split into independent services:

```text
      ┌──────────────────┐
      │  Telegram User   │
      └────────┬─────────┘
               │
               ▼
 ┌───────────────────────┐
 │      Telegram Bot     │
 │                       │
 │  Aiogram              │
 │  FSM                  │
 │  Redis                │
 └──────┬──────────┬─────┘
        │          │
HTTP request    search_request
 / response        │
 (optional)        ▼
        │   ┌───────────┐
        │   │ RabbitMQ  │
        │   └─────┬─────┘
        │         │
        ▼         ▼
 ┌─────────────────────────┐
 │ Marketplace Search      │
 │        Service          │
 │                         │
 │ FastAPI                 │
 │ SearchService           │
 │ TaskManager             │
 │ MarketplaceScraper      │
 │ Playwright              │
 └───────┬─────────┬───────┘
         │         │
         ▼         │
    ┌─────────┐    │
    │ MongoDB │    │
    └─────────┘    │
                   │
           search_result
                   │
                   ▼
           ┌───────────┐
           │ RabbitMQ  │
           └─────┬─────┘
                 │
                 ▼
        ┌─────────────────┐
        │   Telegram Bot  │
        │  Notification   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Telegram User  │
        └─────────────────┘
```

### Service responsibilities

#### Telegram Bot

Responsible for:

- Telegram communication
- User interaction
- FSM conversation flow
- Search configuration
- Sending search requests
- Receiving search results
- Sending notifications to users
- Redis-backed FSM storage

The bot does **not** perform marketplace scraping directly.

#### Marketplace Search Service

Responsible for:

- Marketplace scraping
- Search execution
- Continuous monitoring
- Managing background search tasks
- Database operations
- Providing marketplace region/location data
- Returning search results

The Marketplace Search Service exposes a FastAPI API for HTTP requests such as retrieving
marketplace regions and locations. RabbitMQ is used for asynchronous
communication between the Telegram Bot and Marketplace Search Service, including search
requests and search results.

---

## Communication

The Telegram Bot and Marketplace Search Service communicate primarily through
**RabbitMQ** using asynchronous messages.

- `search_request` — starts a marketplace search.
- `search_result` — delivers newly found listings back to the Telegram Bot.

The Marketplace Search Service also exposes asynchronous **FastAPI** endpoints for operations
such as retrieving marketplace regions and locations. These HTTP requests are
optional; if the Marketplace Search Service is unavailable, the Bot can fall back to retrieving
region data directly.

---

## Search Flow

A typical search works as follows:

```text
1. User starts the Telegram bot
             │
             ▼
2. User selects marketplace
             │
             ▼
3. User selects region/location
             │
             ▼
4. User enters search query
             │
             ▼
5. User specifies maximum price
             │
             ▼
6. User selects search timeout
             │
             ▼
7. Telegram Bot sends search request
             │
             ▼
8. RabbitMQ → search_request
             │
             ▼
9. Marketplace Search Service receives request
             │
             ▼
10. MarketplaceScraper performs search
             │
             ▼
11. New items are detected
             │
             ├──────────────► MongoDB
             │
             ▼
12. RabbitMQ → search_result
             │
             ▼
13. Telegram Bot receives result
             │
             ▼
14. User receives marketplace listing
```

---

## Running with Docker

The project is designed to run as multiple services.

```bash
docker compose up --build
```

This starts the required infrastructure and application services.

To stop the application:

```bash
docker compose down
```

---

## Running Locally

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start infrastructure

Run:

- RabbitMQ
- MongoDB
- Redis

### Start the Marketplace Search Service

```bash
uvicorn main:app --reload
```

### Start the Telegram Bot:

```bash
python main.py
```

---

## Design Principles

The project follows several architectural principles:

- **Separation of responsibilities** — Telegram interaction and marketplace scraping are separate services.
- **Asynchronous communication** — RabbitMQ decouples the Bot and Marketplace Search Service.
- **Dependency injection** — infrastructure dependencies are injected into services.
- **Thin API layer** — FastAPI routes delegate business logic to services.
- **Resource lifecycle management** — Playwright, MongoDB and RabbitMQ are initialized and closed through the application lifecycle.
- **Background task management** — `TaskManager` controls long-running searches.
- **Caching** — Redis reduces unnecessary repeated operations.
- **Configuration through environment variables** — secrets and environment-specific settings are not hard-coded.
- **Testability** — business logic is separated from infrastructure and framework-specific code.

---

## Future Improvements

- Support for additional marketplaces
- Image similarity search
- User search history
- Web dashboard
- Metrics and monitoring

---

## License
MIT — Feel free to use, modify, and share.
