#!/usr/bin/env python3
"""Create Vector Search 2.0 Collection for knowledge storage.

This script creates a Collection in Vertex AI Vector Search 2.0.
It is idempotent - if the Collection already exists, it will be skipped.

Environment Variables:
    GCP_PROJECT_ID: GCP project ID (required)
    GCP_LOCATION: GCP region for Vector Search (default: us-central1)
    COLLECTION_ID: Collection name (default: knowledge)

Usage:
    export GCP_PROJECT_ID=your-project-id
    uv run python scripts/create_collection.py

Prerequisites:
    - gcloud auth application-default login
    - google-cloud-vectorsearch installed
"""

import os
import sys

from google.api_core.exceptions import AlreadyExists
from google.cloud import vectorsearch_v1beta


def get_env_or_exit(name: str) -> str:
    """Get required environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable is required", file=sys.stderr)
        sys.exit(1)
    return value


def create_collection() -> None:
    """Create the knowledge Collection in Vector Search 2.0."""
    project_id = get_env_or_exit("GCP_PROJECT_ID")
    location = os.environ.get("GCP_LOCATION", "us-central1")
    collection_id = os.environ.get("COLLECTION_ID", "knowledge")

    client = vectorsearch_v1beta.VectorSearchServiceClient()
    parent = f"projects/{project_id}/locations/{location}"

    data_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "content": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "user_id": {"type": "string"},
            "source": {"type": "string"},
            "status": {"type": "string"},
            "path": {"type": "string"},
            "created_at": {"type": "string"},
            "updated_at": {"type": "string"},
        },
    }

    vector_schema = {
        "content_embedding": {
            "dense_vector": {
                "dimensions": 768,
                "vertex_embedding_config": {
                    "model_id": "gemini-embedding-001",
                    "text_template": "{title} {content}",
                    "task_type": "RETRIEVAL_DOCUMENT",
                },
            },
        },
    }

    request = vectorsearch_v1beta.CreateCollectionRequest(
        parent=parent,
        collection_id=collection_id,
        collection=vectorsearch_v1beta.Collection(
            data_schema=data_schema,
            vector_schema=vector_schema,
        ),
    )

    try:
        print(f"Creating Collection '{collection_id}' in {location}...")
        operation = client.create_collection(request=request)
        result = operation.result()
        print(f"Collection created successfully: {result.name}")
    except AlreadyExists:
        print(f"Collection '{collection_id}' already exists. Skipping creation.")


if __name__ == "__main__":
    create_collection()
