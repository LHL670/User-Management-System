# Backend Hands-on Practice Demo

This is a RESTful API project implemented based on FastAPI, adopting a Layered Architecture, and includes Docker containerized deployment and complete unit testing.It adopts a Layered Architecture, includes **SQLite** for data persistence, and supports Docker containerized deployment with a multi-stage build.

## 📋 Features

* **RESTful API**: Complete CRUD (Create, Read, Update, Delete) user management functionality.
* **Data Persistence**: Uses **SQLite** with **SQLAlchemy** ORM to ensure data is saved permanently.
* **Frontend Integration**: Serves a **React** Single Page Application (SPA) directly from FastAPI.
* **Batch Processing**: Supports CSV file upload and data import with automatic de-duplication.
* **Data Validation**: Uses Pydantic for strict input validation (null checks, numerical ranges).
* **Documentation Automation**: Integrates Swagger UI for real-time API documentation.
* **Quality Assurance**: Includes Unit Tests covering core logic and edge cases.
* **Containerization**: One-click deployment via Docker (Multi-stage build for Node.js & Python).

---

## 🏗️ System Architecture

This project adopts a **Layered Architecture** to ensure separation of concerns and maintainability.

### Project Directory Tree

```text
project_root/
├── Dockerfile              # [Infra] Multi-stage build (Frontend + Backend)
├── requirements.txt        # [Dependency] Python package list
├── app/                    # [Core] Backend Source Code
│   ├── main.py             # [Entry] App entry, CORS, Static Files serving
│   ├── database/           # [DB] Database connection & session handling
│   │   └── database.py
│   ├── models/             # [Model] Data definitions
│   │   ├── models.py       # Pydantic Schemas (API Layer)
│   │   └── db_models.py    # SQLAlchemy Models (DB Layer)
│   ├── routers/            # [Controller] API route definitions
│   │   └── routers.py
│   └── services/           # [Service] Business logic & Calculation
│       └── user_services.py
├── frontend/               # [UI] React Frontend Source Code
└── tests/                  # [Test] Unit tests
    └── test_api.py
````

### Layer Description

1.  **Entry Point (`main.py`)**: The application entry point. It initializes the database, configures Middleware (CORS), mounts API routers, and **serves the React frontend static files**.
2.  **Router Layer (`routers.py`)**: Handles HTTP requests/responses and defines API Endpoints. It uses Dependency Injection to access the database session.
3.  **Service Layer (`user_services.py`)**: Contains business logic. Handles **CRUD operations via SQLAlchemy**, Pandas calculations, CSV parsing, and de-duplication logic.
4.  **Model Layer**:
      * `models.py`: Defines API schemas (DTOs) and validation rules (e.g., age limits).
      * `db_models.py`: Defines database tables mapping.
5.  **Infrastructure (`database.py`)**: Manages SQLite database connection and session lifecycle.

-----

## 🚀 Start

### Using Docker (Recommended)

This project uses a multi-stage Dockerfile to build the React frontend and setup the Python backend automatically.

1.  **Build Image**

    ```bash
    docker build -t backend_demo .
    ```

2.  **Run Container**

    ```bash
    docker run -p 8000:8000 --name backend_demo-api backend_demo
    ```

3.  **Access Service**

      * **Frontend Dashboard**: [http://localhost:8000/](https://www.google.com/search?q=http://localhost:8000/)
      * **Swagger UI (API Docs)**: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)
      * **API Endpoint**: `http://localhost:8000/users`

-----

## 🧪 Testing

Unit tests are included to verify core logic and exception handling.

**Execute Test Command (Inside Docker):**

```bash
docker exec -it backend_demo-api python -m unittest tests.test_api
```

**Test Cases Covered (Total 7):**

  * **Create User**

      * `test_create_user_success`: Create user successfully.
      * `test_create_duplicate_user`: Duplicate creation check (Expect 409 Conflict).
      * `test_tc1_create_user_empty_name`: Empty name check (Expect 422).
      * `test_tc2_create_user_invalid_age`: Abnormal age check (Expect 422).

  * **Update User**

      * `test_update_user_success`: Update user age successfully.
      * `test_update_user_not_found`: Update non-existent user check (Expect 404 Not Found).
      * `test_update_user_invalid_age`: Update with invalid age check (Expect 422).

<!-- end list -->

```
```