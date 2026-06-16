import os
import json
import httpx
import asyncio

# Setup based on provided credentials
PROJECT_ID = "fc352d688d314602"
API_KEY = "fl_049872a9d847d906ed83d8fb787b96790ec30492689285b6"
BASE_URL = "https://fluxbase.vercel.app/api/execute-sql"

# Using UUIDs for text primary keys since SQLite/Fluxbase might prefer it over auto-increment if distributed

tables = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(255) PRIMARY KEY,
        name TEXT,
        email VARCHAR(255) UNIQUE,
        password_hash TEXT,
        preferences TEXT, -- JSON
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS uploads (
        id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255) REFERENCES users(id),
        filename TEXT,
        type VARCHAR(100), -- text/speech/document
        status VARCHAR(100),
        raw_text TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS extracted_knowledge (
        id VARCHAR(255) PRIMARY KEY,
        upload_id VARCHAR(255) REFERENCES uploads(id),
        knowledge_type VARCHAR(100),
        topic TEXT,
        value_tag TEXT,
        pattern TEXT,
        raw_snippet TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS structured_data (
        id VARCHAR(255) PRIMARY KEY,
        knowledge_id VARCHAR(255) REFERENCES extracted_knowledge(id),
        structured_json TEXT, -- JSON
        agent_version VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS insights (
        id VARCHAR(255) PRIMARY KEY,
        structured_id VARCHAR(255) REFERENCES structured_data(id),
        user_id VARCHAR(255) REFERENCES users(id),
        insight_text TEXT,
        comparison TEXT, -- JSON
        recommendations TEXT, -- JSON
        confidence_score REAL,
        validation_passed BOOLEAN,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS feedback (
        id VARCHAR(255) PRIMARY KEY,
        insight_id VARCHAR(255) REFERENCES insights(id),
        user_id VARCHAR(255) REFERENCES users(id),
        rating VARCHAR(50), -- thumbs_up/thumbs_down
        context_tag TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS confidence_scores (
        id VARCHAR(255) PRIMARY KEY,
        insight_id VARCHAR(255) REFERENCES insights(id),
        retrieval_similarity REAL,
        semantic_relevance REAL,
        consistency_score REAL,
        structural_quality REAL,
        memory_alignment REAL,
        final_score REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS validation_logs (
        id VARCHAR(255) PRIMARY KEY,
        insight_id VARCHAR(255) REFERENCES insights(id),
        check_name VARCHAR(255),
        passed BOOLEAN,
        score REAL,
        failure_reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS visualization_data (
        id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255) REFERENCES users(id),
        chart_type VARCHAR(100),
        chart_data TEXT, -- JSON
        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
]

async def init_db():
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        for sql in tables:
            payload = {
                "projectId": PROJECT_ID,
                "query": sql
            }
            try:
                response = await client.post(BASE_URL, json=payload, headers=headers)
                data = response.json()
                if data.get("success"):
                    print(f"Success running:\n{sql.strip().split('(')[0]}")
                else:
                    print(f"Failed running:\n{sql.strip().split('(')[0]}")
                    print(f"Error details: {data}")
            except Exception as e:
                print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(init_db())
