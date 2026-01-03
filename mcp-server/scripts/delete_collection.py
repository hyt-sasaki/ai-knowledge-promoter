#!/usr/bin/env python3
"""Delete Vector Search 2.0 Collection.

This script deletes a Collection in Vertex AI Vector Search 2.0.
Use this when you need to recreate a Collection with a new schema.

The script will:
1. Delete all data objects in the collection first
2. Then delete the collection itself

Environment Variables:
    GCP_PROJECT_ID: GCP project ID (required)
    GCP_LOCATION: GCP region for Vector Search (default: us-central1)
    COLLECTION_ID: Collection name (default: knowledge)

Usage:
    export GCP_PROJECT_ID=your-project-id
    uv run python scripts/delete_collection.py

Prerequisites:
    - gcloud auth application-default login
    - google-cloud-vectorsearch installed
"""

import os
import sys

from google.api_core.exceptions import NotFound
from google.cloud import vectorsearch_v1beta


def get_env_or_exit(name: str) -> str:
    """Get required environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable is required", file=sys.stderr)
        sys.exit(1)
    return value


def delete_all_data_objects(
    data_client: vectorsearch_v1beta.DataObjectServiceClient,
    search_client: vectorsearch_v1beta.DataObjectSearchServiceClient,
    collection_path: str,
) -> int:
    """Delete all data objects in the collection.

    Returns the number of deleted objects.
    """
    deleted_count = 0

    # Query all data objects (using empty filter to match all)
    request = vectorsearch_v1beta.QueryDataObjectsRequest(
        parent=collection_path,
        page_size=100,
    )

    try:
        while True:
            response = search_client.query_data_objects(request=request)
            if not response.data_objects:
                break

            # Collect IDs to delete
            ids_to_delete = []
            for data_object in response.data_objects:
                # Extract ID from name (format: .../dataObjects/{id})
                data_object_id = data_object.name.split("/")[-1]
                ids_to_delete.append(data_object_id)

            if ids_to_delete:
                # Batch delete - create individual delete requests
                delete_requests = [
                    vectorsearch_v1beta.DeleteDataObjectRequest(
                        name=f"{collection_path}/dataObjects/{obj_id}"
                    )
                    for obj_id in ids_to_delete
                ]
                batch_request = vectorsearch_v1beta.BatchDeleteDataObjectsRequest(
                    parent=collection_path,
                    requests=delete_requests,
                )
                data_client.batch_delete_data_objects(request=batch_request)
                deleted_count += len(ids_to_delete)
                print(f"  Deleted {deleted_count} data objects...")

            # Check for next page
            if not response.next_page_token:
                break
            request.page_token = response.next_page_token
    except NotFound:
        pass

    return deleted_count


def delete_collection() -> None:
    """Delete the knowledge Collection in Vector Search 2.0."""
    project_id = get_env_or_exit("GCP_PROJECT_ID")
    location = os.environ.get("GCP_LOCATION", "us-central1")
    collection_id = os.environ.get("COLLECTION_ID", "knowledge")

    collection_path = (
        f"projects/{project_id}/locations/{location}/collections/{collection_id}"
    )

    vs_client = vectorsearch_v1beta.VectorSearchServiceClient()
    data_client = vectorsearch_v1beta.DataObjectServiceClient()
    search_client = vectorsearch_v1beta.DataObjectSearchServiceClient()

    try:
        # Step 1: Delete all data objects
        print(f"Deleting all data objects in '{collection_id}'...")
        deleted_count = delete_all_data_objects(
            data_client, search_client, collection_path
        )
        print(f"  Total deleted: {deleted_count} data objects.")

        # Step 2: Delete the collection
        print(f"Deleting Collection '{collection_id}' in {location}...")
        operation = vs_client.delete_collection(name=collection_path)
        operation.result()
        print(f"Collection '{collection_id}' deleted successfully.")
    except NotFound:
        print(f"Collection '{collection_id}' not found. Nothing to delete.")


if __name__ == "__main__":
    delete_collection()
