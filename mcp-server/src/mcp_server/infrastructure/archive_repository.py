"""Vector Search 2.0 implementation of ArchivedKnowledgeRepository.

Skeleton implementation for Phase 2. Full implementation in Phase 3.
"""

import os

from ..domain.models import ArchivedKnowledge


def _get_project_id() -> str | None:
    """Get GCP project ID from environment or metadata server."""
    # First try environment variable
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return project_id

    # Try GOOGLE_CLOUD_PROJECT (set by Cloud Run)
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return project_id

    # Try GCP metadata server (for Cloud Run / GCE)
    try:
        import urllib.request

        req = urllib.request.Request(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read().decode("utf-8")
    except Exception:
        pass

    return None


class VectorSearchArchivedKnowledgeRepository:
    """Archived knowledge repository using Vertex AI Vector Search 2.0.

    Skeleton implementation for Phase 2.
    Full implementation with actual DB operations in Phase 3.
    """

    def __init__(
        self,
        project_id: str | None = None,
        location: str | None = None,
        collection_id: str = "archived-knowledge",
    ):
        """Initialize the repository.

        Args:
            project_id: GCP project ID (auto-detected if not provided)
            location: GCP location (defaults to GCP_LOCATION env var or us-central1)
            collection_id: Collection ID (defaults to "archived-knowledge")
        """
        self.project_id = project_id or _get_project_id()
        self.location = location or os.environ.get("GCP_LOCATION", "us-central1")
        self.collection_id = collection_id

        if not self.project_id:
            raise ValueError(
                "project_id must be provided or detectable from environment"
            )

        self._collection_path = (
            f"projects/{self.project_id}/locations/{self.location}"
            f"/collections/{self.collection_id}"
        )

    def save(self, archived: ArchivedKnowledge) -> ArchivedKnowledge:
        """Save archived knowledge.

        Args:
            archived: The archived knowledge to save

        Returns:
            The saved archived knowledge

        Note:
            Skeleton implementation - returns input as-is.
            Full implementation in Phase 3.
        """
        # Skeleton: return input as-is (no actual DB operation)
        return archived

    def get(self, id: str) -> ArchivedKnowledge | None:
        """Get archived knowledge by ID.

        Args:
            id: Archived knowledge identifier (original knowledge ID)

        Returns:
            ArchivedKnowledge if found, None otherwise

        Note:
            Skeleton implementation - returns None.
            Full implementation in Phase 3.
        """
        # Skeleton: return None (not implemented)
        return None
