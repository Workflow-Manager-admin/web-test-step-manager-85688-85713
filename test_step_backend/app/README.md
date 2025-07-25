# Test Step Backend Application

## Setup

1. Install dependencies:

    pip install -r requirements.txt

2. Initialize Database:

    ```
    from app import app, db
    with app.app_context():
        db.create_all()
    ```

   Alternatively, use Flask-Migrate for migrations (recommended for production).

3. Run the server:

    ```
    python run.py
    ```

## API Overview

- `/auth/signup`    : Register new users.
- `/auth/login`     : Obtain JWT.
- `/steps/`         : CRUD, list, search test steps (JWT required).
- `/suites/`        : CRUD, list suites (JWT required).

## Environment Variables

- `DATABASE_URL` (default: sqlite:///test_step_backend.db)
- `SECRET_KEY`    (default: dev_secret, override for prod!)
