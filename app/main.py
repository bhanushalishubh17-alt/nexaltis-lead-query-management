import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, engine
from app.routers import ai, analytics, leads, queries

load_dotenv()

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)


def ensure_sqlite_columns():
    """Add new assessment feature columns when running against an existing SQLite DB."""
    with engine.begin() as connection:
        lead_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(leads)")).fetchall()
        }
        query_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(queries)")).fetchall()
        }

        if "lead_score" not in lead_columns:
            connection.execute(text("ALTER TABLE leads ADD COLUMN lead_score INTEGER DEFAULT 0 NOT NULL"))
        if "priority" not in lead_columns:
            connection.execute(text("ALTER TABLE leads ADD COLUMN priority VARCHAR(50) DEFAULT 'Cold' NOT NULL"))

        query_column_definitions = {
            "category": "VARCHAR(100)",
            "intent": "VARCHAR(100)",
            "summary": "TEXT",
            "suggested_response": "TEXT",
            "ai_provider": "VARCHAR(50) DEFAULT 'rule_based' NOT NULL",
        }
        for column_name, column_definition in query_column_definitions.items():
            if column_name not in query_columns:
                connection.execute(
                    text(f"ALTER TABLE queries ADD COLUMN {column_name} {column_definition}")
                )


ensure_sqlite_columns()

app = FastAPI(
    title="NexAltis Lead & Query Management System",
    description=(
        "A lightweight backend system for managing customer inquiries, "
        "tracking leads, and monitoring follow-ups for NexAltis Technologies LLP."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(queries.router)
app.include_router(analytics.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "NexAltis Lead & Query Management System",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
