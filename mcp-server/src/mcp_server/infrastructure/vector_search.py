"""Vector Search 2.0 implementation of KnowledgeRepository."""

import os
import uuid
from datetime import UTC, datetime

from google.cloud import vectorsearch_v1beta

from ..domain.models import Knowledge, SearchResult


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


class VectorSearchKnowledgeRepository:
    """Knowledge repository using Vertex AI Vector Search 2.0.

    This implementation uses Vector Search 2.0's Collection API with
    auto-embeddings for semantic search capabilities.
    """

    def __init__(
        self,
        project_id: str | None = None,
        location: str | None = None,
        collection_id: str = "knowledge",
    ):
        """Initialize the repository.

        Args:
            project_id: GCP project ID (auto-detected if not provided)
            location: GCP location (defaults to GCP_LOCATION env var or us-central1)
            collection_id: Collection ID (defaults to "knowledge")
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
        self._search_client = vectorsearch_v1beta.DataObjectSearchServiceClient()

    def save(self, knowledge: Knowledge) -> Knowledge:
        """Save knowledge to Vector Search Collection.

        Args:
            knowledge: The knowledge to save

        Returns:
            The saved knowledge with ID and timestamps populated
        """
        now = datetime.now(UTC)

        # Generate ID if not provided
        knowledge_id = knowledge.id if knowledge.id else str(uuid.uuid4())

        # Set timestamps
        created_at = knowledge.created_at or now
        updated_at = now

        # Prepare data object
        data = {
            "id": knowledge_id,
            "title": knowledge.title,
            "content": knowledge.content,
            "tags": knowledge.tags,
            "user_id": knowledge.user_id,
            "source": knowledge.source,
            "status": knowledge.status,
            "github_path": knowledge.github_path,
            "pr_url": knowledge.pr_url,
            "promoted_from_id": knowledge.promoted_from_id,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
        }

        request = vectorsearch_v1beta.CreateDataObjectRequest(
            parent=self._collection_path,
            data_object_id=knowledge_id,
            data_object=vectorsearch_v1beta.DataObject(
                data=data,
                vectors={},  # Auto-Embeddings will generate vectors
            ),
        )

        self._data_object_client.create_data_object(request=request)

        # Return updated knowledge
        return Knowledge(
            id=knowledge_id,
            title=knowledge.title,
            content=knowledge.content,
            tags=knowledge.tags,
            user_id=knowledge.user_id,
            source=knowledge.source,
            status=knowledge.status,
            github_path=knowledge.github_path,
            pr_url=knowledge.pr_url,
            promoted_from_id=knowledge.promoted_from_id,
            created_at=created_at,
            updated_at=updated_at,
        )

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
    ) -> SearchResult:
        """Search knowledge using semantic search.

        Args:
            query: Search query text
            limit: Maximum number of results (default: 20)

        Returns:
            SearchResult containing matching items
        """
        request = vectorsearch_v1beta.SearchDataObjectsRequest(
            parent=self._collection_path,
            semantic_search=vectorsearch_v1beta.SemanticSearch(
                search_text=query,
                search_field="content_embedding",
                task_type="QUESTION_ANSWERING",
                top_k=limit,
                output_fields=vectorsearch_v1beta.OutputFields(
                    data_fields=[
                        "id",
                        "title",
                        "content",
                        "tags",
                        "user_id",
                        "source",
                        "status",
                        "github_path",
                        "pr_url",
                        "promoted_from_id",
                        "created_at",
                        "updated_at",
                    ]
                ),
            ),
        )

        response = self._search_client.search_data_objects(request=request)

        items = []
        for result in response.results:
            data = result.data_object.data
            items.append(
                Knowledge(
                    id=data.get("id", ""),
                    title=data.get("title", ""),
                    content=data.get("content", ""),
                    tags=list(data.get("tags", [])),
                    user_id=data.get("user_id", "anonymous"),
                    source=data.get("source", "personal"),
                    status=data.get("status", "draft"),
                    github_path=data.get("github_path", ""),
                    pr_url=data.get("pr_url", ""),
                    promoted_from_id=data.get("promoted_from_id", ""),
                    created_at=self._parse_datetime(data.get("created_at")),
                    updated_at=self._parse_datetime(data.get("updated_at")),
                    score=result.distance if hasattr(result, "distance") else None,
                )
            )

        return SearchResult(items=items, total=len(items))

    def get(self, id: str) -> Knowledge | None:
        """Get knowledge by ID.

        Args:
            id: Knowledge identifier

        Returns:
            Knowledge if found, None otherwise
        """
        try:
            request = vectorsearch_v1beta.GetDataObjectRequest(
                name=f"{self._collection_path}/dataObjects/{id}"
            )
            response = self._data_object_client.get_data_object(request=request)
            data = response.data

            return Knowledge(
                id=data.get("id", ""),
                title=data.get("title", ""),
                content=data.get("content", ""),
                tags=list(data.get("tags", [])),
                user_id=data.get("user_id", "anonymous"),
                source=data.get("source", "personal"),
                status=data.get("status", "draft"),
                github_path=data.get("github_path", ""),
                pr_url=data.get("pr_url", ""),
                promoted_from_id=data.get("promoted_from_id", ""),
                created_at=self._parse_datetime(data.get("created_at")),
                updated_at=self._parse_datetime(data.get("updated_at")),
            )
        except Exception:
            # Not found or other error
            return None

    def delete(self, id: str) -> bool:
        """Delete knowledge by ID.

        Args:
            id: Knowledge identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            request = vectorsearch_v1beta.DeleteDataObjectRequest(
                name=f"{self._collection_path}/dataObjects/{id}"
            )
            self._data_object_client.delete_data_object(request=request)
            return True
        except Exception:
            # Not found or other error
            return False

    def find_by_github_path(self, path: str) -> Knowledge | None:
        """Find knowledge by GitHub file path.

        Args:
            path: GitHub file path

        Returns:
            Knowledge if found, None otherwise

        Note:
            Skeleton implementation - returns None.
            Full implementation in Phase 3.
        """
        # Skeleton: return None (not implemented)
        return None

    def find_by_pr_url(self, url: str) -> Knowledge | None:
        """Find knowledge by PR URL.

        Args:
            url: Pull request URL

        Returns:
            Knowledge if found, None otherwise

        Note:
            Skeleton implementation - returns None.
            Full implementation in Phase 3.
        """
        # Skeleton: return None (not implemented)
        return None

    def update_status(
        self, id: str, status: str, *, pr_url: str = ""
    ) -> Knowledge | None:
        """Update knowledge status.

        Args:
            id: Knowledge identifier
            status: New status ("draft", "proposed", "promoted")
            pr_url: PR URL (optional, for proposed status)

        Returns:
            Updated knowledge if found, None otherwise
        """
        # Get existing knowledge
        knowledge = self.get(id)
        if knowledge is None:
            return None

        now = datetime.now(UTC)

        # Build update data (only fields that change)
        update_data = {
            "status": status,
            "updated_at": now.isoformat(),
        }
        if pr_url:
            update_data["pr_url"] = pr_url

        # Use update API to safely update in place
        request = vectorsearch_v1beta.UpdateDataObjectRequest(
            data_object=vectorsearch_v1beta.DataObject(
                name=f"{self._collection_path}/dataObjects/{id}",
                data=update_data,
            ),
        )

        self._data_object_client.update_data_object(request=request)

        # Return updated knowledge object
        return Knowledge(
            id=knowledge.id,
            title=knowledge.title,
            content=knowledge.content,
            tags=knowledge.tags,
            user_id=knowledge.user_id,
            source=knowledge.source,
            status=status,
            github_path=knowledge.github_path,
            pr_url=pr_url if pr_url else knowledge.pr_url,
            promoted_from_id=knowledge.promoted_from_id,
            created_at=knowledge.created_at,
            updated_at=now,
        )

    def _parse_datetime(self, value: str | None) -> datetime | None:
        """Parse ISO 8601 datetime string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
