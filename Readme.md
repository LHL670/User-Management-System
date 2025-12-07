# Backend Hands-on Practice Demo

This is a RESTful API project implemented based on **FastAPI**, adopting a Layered Architecture, and includes Docker containerized deployment and complete unit testing.

## 📋 Features

  * **RESTful API**: Complete CRUD user management functionality.
  * **Batch Processing**: Supports CSV file upload and data import, equipped with an automatic de-duplication mechanism.
  * **Data Validation**: Uses Pydantic for input validation (null checks, numerical ranges).
  * **Documentation Automation**: Integrates Swagger UI to provide real-time API documentation.
  * **Quality Assurance**: Includes Unit Tests, covering core logic and edge cases.
  * **Containerization**: Supports one-click deployment via Docker.

-----

## 🏗️ System Architecture

This project adopts a **Layered Architecture** to ensure separation of concerns and code maintainability.

### Project Directory Tree

```text
project_root/
├── Dockerfile              # [Infra] Container deployment settings
├── requirements.txt        # [Dependency] Python package list
├── app/                    # [Core] Core code
│   ├── main.py             # [Entry] Application entry point and CORS settings
│   ├── models/             # [Model] Data definition and validation
│   │   └── models.py
│   ├── routers/            # [Controller] API route definition
│   │   └── routers.py
│   └── services/           # [Service] Logic and calculation
│       └── user_services.py
└── tests/                  # [Test] Unit tests
    └── test_api.py
```

### Layer Description

1.  **Entry Point (`main.py`)**: The entry point of the application, responsible for starting the FastAPI instance, configuring Middleware (CORS), and mounting routers.
2.  **Router Layer (`routers.py`)**: Responsible for handling HTTP requests and responses, defining API Endpoints.
3.  **Service Layer (`user_services.py`)**: The logic layer. Handles database operations (In-Memory), Pandas calculations, CSV parsing, and de-duplication logic.
4.  **Model Layer (`models.py`)**: Defines data Schemas. Includes `UserCreate` and `UserResponse`, and implements validation rules for TC1 (empty name) and TC2 (abnormal age).

-----

## 🚀 Start

### Using Docker

1.  **Build Image**

    ```bash
    docker build -t backend_demo .
    ```

2.  **Run Container**

    ```bash
    docker run -p 8000:8000 --name backend_demo-api backend_demo
    ```

3.  **Access Service**

      * Swagger UI (API Documentation): [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)
      * API Endpoint: `http://localhost:8000/users`

-----

## 🧪 Testing

Verify normal flows and exception handling.

**Execute Test Command (Inside Docker):**

```bash
docker exec -it backend_demo-api python -m unittest tests.test_api
```

**Test Cases Covered:**

  * `test_create_user_success`: Create user successfully.
  * `test_create_duplicate_user`: Duplicate creation check (Expect 409 Conflict).
  * `test_tc1_create_user_empty_name`: Empty name check (Expect 422).
  * `test_tc2_create_user_invalid_age`: Abnormal age check (Expect 422).