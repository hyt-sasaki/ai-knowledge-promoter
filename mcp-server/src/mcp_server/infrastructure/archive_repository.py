"""Vector Search 2.0 implementation of ArchivedKnowledgeRepository."""

import os
from datetime import UTC, datetime

from google.cloud import vectorsearch_v1beta

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

    Stores archived knowledge for audit trail when personal knowledge
    is promoted to team knowledge.
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

        # Initialize client
        self._data_object_client = vectorsearch_v1beta.DataObjectServiceClient()

    def save(self, archived: ArchivedKnowledge) -> ArchivedKnowledge:
        """Save archived knowledge to Vector Search Collection.

        Args:
            archived: The archived knowledge to save

        Returns:
            The saved archived knowledge with timestamps populated
        """
        now = datetime.now(UTC)

        # Set timestamps
        archived_at = archived.archived_at or now

        # Prepare data object
        data = {
            "id": archived.id,
            "title": archived.title,
            "content": archived.content,
            "tags": archived.tags,
            "user_id": archived.user_id,
            "promoted_to_id": archived.promoted_to_id,
            "archived_at": archived_at.isoformat(),
            "original_created_at": (
                archived.original_created_at.isoformat()
                if archived.original_created_at
                else None
            ),
        }

        request = vectorsearch_v1beta.CreateDataObjectRequest(
            parent=self._collection_path,
            data_object_id=archived.id,
            data_object=vectorsearch_v1beta.DataObject(
                data=data,
                vectors={},  # Auto-Embeddings will generate vectors
            ),
        )

        self._data_object_client.create_data_object(request=request)

        # Return updated archived knowledge
        return ArchivedKnowledge(
            id=archived.id,
            title=archived.title,
            content=archived.content,
            tags=archived.tags,
            user_id=archived.user_id,
            promoted_to_id=archived.promoted_to_id,
            archived_at=archived_at,
            original_created_at=archived.original_created_at,
        )

    def get(self, id: str) -> ArchivedKnowledge | None:
        """Get archived knowledge by ID.

        Args:
            id: Archived knowledge identifier (original knowledge ID)

        Returns:
            ArchivedKnowledge if found, None otherwise
        """
        try:
            request = vectorsearch_v1beta.GetDataObjectRequest(
                name=f"{self._collection_path}/dataObjects/{id}"
            )
            response = self._data_object_client.get_data_object(request=request)
            data = response.data

            return ArchivedKnowledge(
                id=id,
                title=data.get("title", ""),
                content=data.get("content", ""),
                tags=list(data.get("tags", [])),
                user_id=data.get("user_id", "anonymous"),
                promoted_to_id=data.get("promoted_to_id", ""),
                archived_at=self._parse_datetime(data.get("archived_at")),
                original_created_at=self._parse_datetime(
                    data.get("original_created_at")
                ),
            )
        except Exception:
            # Not found or other error
            return None

    def _parse_datetime(self, value: str | None) -> datetime | None:
        """Parse ISO 8601 datetime string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
