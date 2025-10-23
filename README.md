# Backend Wizards — Stage 1: String Analyzer Service

Welcome to the **String Analyzer API**, developed for Stage 1 of the Backend Wizards cohort. This service analyzes strings, computes their properties, stores them, and allows retrieval through both **RESTful endpoints** and **natural language queries**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [How the Problem Was Solved](#how-the-problem-was-solved)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Testing](#testing)
- [Deployment](#deployment)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [Author](#author)

---

## Project Overview

The project was designed to meet the Stage 1 requirements:

- Analyze and store strings with computed properties.
- Support **CRUD operations** via REST endpoints.
- Allow **filtering** by properties such as palindrome status, length, word count, or character presence.
- Support **natural language queries**, allowing users to ask for strings in plain English (e.g., "all single word palindromic strings").

---

## Key Features

Each analyzed string stores the following:

- `length` – Number of characters.
- `is_palindrome` – Boolean indicating if the string reads the same forwards and backwards (case-insensitive).
- `unique_characters` – Count of distinct characters.
- `word_count` – Number of words in the string.
- `sha256_hash` – Unique identifier generated from the string.
- `character_frequency_map` – Dictionary mapping each character to its occurrence count.

Endpoints also include **full CRUD operations** and **advanced filtering**.

---

## How the Problem Was Solved

1. **String Analysis Logic**
   - Implemented in Python using **FastAPI** for REST endpoints.
   - Palindrome detection and character frequency analysis are case-insensitive.
   - SHA-256 is used for unique string identification.

2. **Data Storage**
   - Stored in a **PostgreSQL database** (or SQLite for local testing).
   - SQLAlchemy ORM handles models and queries.

3. **Filtering**
   - Query parameters allow filtering by:
     - `min_length` / `max_length`
     - `word_count`
     - `contains_character`
     - `is_palindrome`
   - Combined filters support multiple constraints simultaneously.

4. **Natural Language Query Parsing**
   - Implemented using **Lark** grammar and a custom **Transformer**.
   - Queries like `"all palindromic strings longer than 5 letters"` are parsed into SQLAlchemy filters.
   - Handles numeric constraints, boolean flags, and character heuristics.

5. **Error Handling**
   - 400 Bad Request for invalid input.
   - 404 Not Found for non-existent strings.
   - 409 Conflict for duplicate strings.
   - 422 Unprocessable Entity for conflicting or invalid queries.

6. **Deployment**
   - Hosted on [Your Deployment URL] using [Railway/Heroku/AWS/etc.].
   - Supports HTTPS and is fully testable from multiple networks.

---

## API Endpoints

### 1. Create/Analyze String

```
POST /strings
Content-Type: application/json
Body: { "value": "string to analyze" }
```

**Response 201 Created:**

```json
{
  "id": "sha256_hash_value",
  "value": "string to analyze",
  "properties": { ... },
  "created_at": "2025-08-27T10:00:00Z"
}
```

---

### 2. Get Specific String

```
GET /strings/{string_value}
```

**Response 200 OK:**

```json
{
  "id": "sha256_hash_value",
  "value": "requested string",
  "properties": { ... },
  "created_at": "2025-08-27T10:00:00Z"
}
```

---

### 3. Get All Strings With Filtering

```
GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
```

**Response 200 OK:**

```json
{
  "data": [ ... ],
  "count": 15,
  "filters_applied": { ... }
}
```

---

### 4. Natural Language Filtering

```
GET /strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings
```

**Response 200 OK:**

```json
{
  "data": [ ... ],
  "count": 3,
  "interpreted_query": {
    "original": "all single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true
    }
  }
}
```

---

### 5. Delete String

```
DELETE /strings/{string_value}
```

**Response 204 No Content**

---

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/string-analyzer-api.git
cd string-analyzer-api

# Use Poetry to install dependencies
poetry install
```

---

## Running Locally

```bash
# Activate poetry shell
poetry shell

# Set environment variables if needed
export DATABASE_URL=sqlite:///local.db  # or PostgreSQL URL

# Run the API server
uvicorn app.main:app --reload
```

- Access API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Testing

- Test endpoints via **Postman** or **Swagger UI**.
- Ensure strings are analyzed, stored, and filtered correctly.
- Validate natural language query parsing for complex queries.

---

## Deployment

- Deployed using [Railway/Heroku/AWS/etc.] at: [Your Deployment URL]
- Ensure all environment variables (DB, secrets) are configured in the hosting service.

---

## Tech Stack

- **Language:** Python 3.12
- **Web Framework:** FastAPI
- **Database:** PostgreSQL 
- **ORM:** SQLAlchemy
- **Parsing NLP:** Lark
- **Hashing:** hashlib (SHA-256)
- **Deployment:** Railway

---

## Contributing

- Fork the repository
- Create a feature branch
- Open a pull request with description

---

## Author

**Faruq Alabi Bashir**  
Email: [your-email@example.com]  
GitHub: [https://github.com/yourusername](https://github.com/yourusername)