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

    This implementation uses Vector Search 2.0's Collection API
    for storing archived knowledge after promotion.
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

        # Initialize clients
        self._data_object_client = vectorsearch_v1beta.DataObjectServiceClient()

    def save(self, archived: ArchivedKnowledge) -> ArchivedKnowledge:
        """Save archived knowledge to Vector Search Collection.

        Args:
            archived: The archived knowledge to save

        Returns:
            The saved archived knowledge with timestamps populated
        """
        now = datetime.now(UTC)

        # Set archived_at if not provided
        archived_at = archived.archived_at or now

        # Prepare data object
        data = {
            "id": archived.id,
            "title": archived.title,
            "content": archived.content,
            "tags": archived.tags,
            "user_id": archived.user_id,
            "source": archived.source,
            "status": archived.status,
            "github_path": archived.github_path,
            "pr_url": archived.pr_url,
            "promoted_from_id": archived.promoted_from_id,
            "created_at": archived.created_at.isoformat() if archived.created_at else now.isoformat(),
            "updated_at": archived.updated_at.isoformat() if archived.updated_at else now.isoformat(),
            "archived_at": archived_at.isoformat(),
            "promoted_to_id": archived.promoted_to_id,
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
            source=archived.source,
            status=archived.status,
            github_path=archived.github_path,
            pr_url=archived.pr_url,
            promoted_from_id=archived.promoted_from_id,
            created_at=archived.created_at,
            updated_at=archived.updated_at,
            archived_at=archived_at,
            promoted_to_id=archived.promoted_to_id,
        )

    def get(self, id: str) -> ArchivedKnowledge | None:
        """Get archived knowledge by original ID.

        Args:
            id: Original knowledge identifier

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
                id=data.get("id", ""),
                title=data.get("title", ""),
                content=data.get("content", ""),
                tags=list(data.get("tags", [])),
                user_id=data.get("user_id", "anonymous"),
                source=data.get("source", "personal"),
                status=data.get("status", "proposed"),
                github_path=data.get("github_path", ""),
                pr_url=data.get("pr_url", ""),
                promoted_from_id=data.get("promoted_from_id", ""),
                created_at=self._parse_datetime(data.get("created_at")),
                updated_at=self._parse_datetime(data.get("updated_at")),
                archived_at=self._parse_datetime(data.get("archived_at")),
                promoted_to_id=data.get("promoted_to_id", ""),
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
