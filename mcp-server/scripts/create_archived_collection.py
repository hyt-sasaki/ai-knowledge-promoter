#!/usr/bin/env python3
"""Create Vector Search 2.0 Collection for archived knowledge storage.

This script creates an archived-knowledge Collection in Vertex AI Vector Search 2.0.
It is idempotent - if the Collection already exists, it will be skipped.

The archived-knowledge Collection stores knowledge that has been promoted to team
knowledge. It serves as an audit trail and allows for potential restoration.

Environment Variables:
    GCP_PROJECT_ID: GCP project ID (required)
    GCP_LOCATION: GCP region for Vector Search (default: us-central1)
    COLLECTION_ID: Collection name (default: archived-knowledge)

Usage:
    export GCP_PROJECT_ID=your-project-id
    uv run python scripts/create_archived_collection.py

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


def create_archived_collection() -> None:
    """Create the archived-knowledge Collection in Vector Search 2.0."""
    project_id = get_env_or_exit("GCP_PROJECT_ID")
    location = os.environ.get("GCP_LOCATION", "us-central1")
    collection_id = os.environ.get("COLLECTION_ID", "archived-knowledge")

    client = vectorsearch_v1beta.VectorSearchServiceClient()
    parent = f"projects/{project_id}/locations/{location}"

    # ArchivedKnowledge data schema
    # Based on design.md specification
    data_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},  # Original knowledge ID
            "title": {"type": "string"},
            "content": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "user_id": {"type": "string"},
            "promoted_to_id": {"type": "string"},  # ID of promoted team knowledge
            "archived_at": {"type": "string"},  # Archive timestamp (ISO 8601)
            "original_created_at": {"type": "string"},  # Original creation timestamp
        },
    }

    # No vector schema for archived collection
    # Archived knowledge is not searchable by semantic search
    # It's only for audit trail and potential restoration

    request = vectorsearch_v1beta.CreateCollectionRequest(
        parent=parent,
        collection_id=collection_id,
        collection=vectorsearch_v1beta.Collection(
            data_schema=data_schema,
            # No vector_schema - archived knowledge doesn't need embeddings
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
    create_archived_collection()
