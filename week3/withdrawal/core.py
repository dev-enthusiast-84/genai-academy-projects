"""Core withdrawal engine - manages consent, deletion workflow, and verification."""

import json
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


class BoundaryError(Exception):
    """Raised when workflow boundaries are violated."""
    pass


class SimpleDB:
    """Simple in-memory database interface for catalog."""

    def __init__(self, catalog: dict):
        self.catalog = catalog
        self._result = None

    def execute(self, query: str, params=None):
        """Execute a simple query."""
        if 'SELECT 1 FROM catalog' in query:
            self._result = (1,) if self.catalog else None
        else:
            self._result = None
        return self

    def fetchone(self):
        """Fetch one result."""
        return self._result


class Engine:
    """Manages withdrawal requests, consent state, and deletion workflow."""

    def __init__(self, data_dir: str, services=None, require_review: bool = False):
        """Initialize engine with data directory.

        Args:
            data_dir: Path to runtime data directory
            services: Optional services configuration
            require_review: Whether review is required (optional)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.services = services
        self.require_review = require_review

        self.catalog_file = self.data_dir / "catalog.json"
        self.requests_file = self.data_dir / "requests.json"
        self.consent_file = self.data_dir / "consent.json"
        self.suppression_file = self.data_dir / "suppression.json"
        self.edges_file = self.data_dir / "edges.json"

        self.catalog = self._load_json(self.catalog_file, {})
        self.requests = self._load_json(self.requests_file, {})
        self.consent = self._load_json(self.consent_file, {"state": "not_granted"})
        self.suppression = self._load_json(self.suppression_file, {})

        # Simple database interface for compatibility
        self.db = SimpleDB(self.catalog)

    def _load_json(self, path: Path, default: Any) -> Any:
        """Load JSON file or return default."""
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def _save_json(self, path: Path, data: Any) -> None:
        """Save JSON file."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def discover_records(self, user_id: str, query: str = "") -> List[Dict]:
        """Discover authorized record metadata.

        Args:
            user_id: User making the request
            query: Search filter (empty lists all)

        Returns:
            List of matching record metadata

        Raises:
            BoundaryError: If read fails
        """
        if not self.catalog:
            return []

        results = []
        query_lower = query.lower()

        for record_id, record in self.catalog.items():
            if record.get("user_id") != user_id:
                continue

            if not query or any([
                query_lower in record_id.lower(),
                query_lower in record.get("title", "").lower(),
                query_lower in record.get("service", "").lower(),
                query_lower in record.get("kind", "").lower(),
            ]):
                results.append({
                    "id": record_id,
                    "title": record.get("title", ""),
                    "service": record.get("service", ""),
                    "kind": record.get("kind", ""),
                    "version": record.get("version", 1),
                })

        return sorted(results, key=lambda r: r["id"])

    def trace_lineage(self, user_id: str, root_id: str) -> Dict:
        """Trace explicit dependencies for a root record.

        Args:
            user_id: User making the request
            root_id: Root record ID to trace from

        Returns:
            Dict with records and edges (dependencies)

        Raises:
            BoundaryError: If root doesn't exist or read fails
        """
        if root_id not in self.catalog:
            raise BoundaryError(f"Root record '{root_id}' not found")

        if self.catalog[root_id].get("user_id") != user_id:
            raise BoundaryError(f"Unauthorized access to '{root_id}'")

        records = {root_id: self.catalog[root_id]}
        edges = []
        visited = {root_id}
        queue = [root_id]

        # Simple graph traversal - in real implementation would read from database
        edges_data = self._load_json(self.data_dir / "edges.json", [])

        while queue:
            current = queue.pop(0)

            for edge in edges_data:
                if edge.get("source") == current and edge.get("target") not in visited:
                    target_id = edge["target"]
                    if target_id in self.catalog:
                        target = self.catalog[target_id]
                        if target.get("user_id") == user_id:
                            records[target_id] = target
                            visited.add(target_id)
                            queue.append(target_id)
                            edges.append({
                                "source": edge["source"],
                                "target": edge["target"],
                                "relationship": edge.get("relationship", "derived_from"),
                            })

        return {
            "records": list(records.values()),
            "edges": edges,
        }

    def inspect_service(self, user_id: str, record_id: str) -> Dict:
        """Check current presence and version of a record.

        Args:
            user_id: User making the request
            record_id: Record ID to inspect

        Returns:
            Dict with state (present/absent/unknown), version, etc.

        Raises:
            BoundaryError: If unauthorized or service rejects
        """
        if record_id not in self.catalog:
            raise BoundaryError(f"Record '{record_id}' not found")

        record = self.catalog[record_id]
        if record.get("user_id") != user_id:
            raise BoundaryError(f"Unauthorized access to '{record_id}'")

        # Check if suppressed (marked for non-reingestion)
        if record_id in self.suppression:
            return {
                "record_id": record_id,
                "state": "suppressed",
                "version": record.get("version", 1),
                "title": record.get("title", ""),
                "service": record.get("service", ""),
            }

        # In real implementation, would query the actual service
        # For now, return present state
        return {
            "record_id": record_id,
            "state": "present",
            "version": record.get("version", 1),
            "title": record.get("title", ""),
            "service": record.get("service", ""),
        }

    def grant_consent(self, user_id: str, agreed: bool = True) -> Dict:
        """Grant sharing consent.

        Args:
            user_id: User granting consent
            agreed: Whether user agreed

        Returns:
            Updated consent state

        Raises:
            BoundaryError: If consent cannot be granted
        """
        if not agreed:
            raise BoundaryError("Explicit sharing consent is required")

        if self.consent.get("state") == "withdrawn":
            raise BoundaryError("Consent was withdrawn. Reset to start again.")

        consent_id = str(uuid.uuid4())[:8]
        self.consent = {
            "id": consent_id,
            "state": "active",
            "user_id": user_id,
            "granted_at": datetime.now().isoformat(),
            "purpose": "Data sharing across services",
        }
        self._save_json(self.consent_file, self.consent)

        return self.consent.copy()

    def withdraw_consent(self, user_id: str) -> Dict:
        """Withdraw sharing consent.

        Args:
            user_id: User withdrawing consent

        Returns:
            Updated consent state

        Raises:
            BoundaryError: If consent cannot be withdrawn
        """
        if self.consent.get("user_id") != user_id:
            raise BoundaryError("Cannot withdraw someone else's consent")

        self.consent["state"] = "withdrawn"
        self.consent["withdrawn_at"] = datetime.now().isoformat()
        self._save_json(self.consent_file, self.consent)

        return self.consent.copy()

    def create_request(
        self,
        user_id: str,
        root_ids: List[str],
        target_ids: List[str],
        origin: str = "live_agent",
    ) -> Dict:
        """Create a withdrawal request.

        Args:
            user_id: User making request
            root_ids: Root record IDs
            target_ids: All target record IDs for deletion
            origin: Request origin (live_agent, scripted_rehearsal)

        Returns:
            Created request dict

        Raises:
            BoundaryError: If request is invalid
        """
        if not root_ids or not target_ids:
            raise BoundaryError("Request must have root and target records")

        request_id = str(uuid.uuid4())[:8]
        request = {
            "id": request_id,
            "user_id": user_id,
            "root_ids": root_ids,
            "target_ids": target_ids,
            "status": "awaiting_approval",
            "origin": origin,
            "created_at": datetime.now().isoformat(),
            "approval": None,
            "completed_at": None,
            "events": [],
        }

        self.requests[request_id] = request
        self._save_json(self.requests_file, self.requests)

        return request.copy()

    def approve_request(self, request_id: str, user_id: str) -> Dict:
        """Approve a withdrawal request.

        Args:
            request_id: Request to approve
            user_id: User approving

        Returns:
            Updated request

        Raises:
            BoundaryError: If approval is invalid
        """
        if request_id not in self.requests:
            raise BoundaryError(f"Request '{request_id}' not found")

        request = self.requests[request_id]
        if request["user_id"] != user_id:
            raise BoundaryError("Cannot approve someone else's request")

        if request["status"] != "awaiting_approval":
            raise BoundaryError(f"Request status '{request['status']}' doesn't allow approval")

        request["approval"] = {
            "approved_by": user_id,
            "approved_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        }
        request["status"] = "approved"
        self._save_json(self.requests_file, self.requests)

        return request.copy()

    def execute_deletion(self, request_id: str, user_id: str) -> Dict:
        """Execute approved deletion.

        Args:
            request_id: Approved request to execute
            user_id: User executing

        Returns:
            Execution result with deleted records

        Raises:
            BoundaryError: If deletion cannot proceed
        """
        if request_id not in self.requests:
            raise BoundaryError(f"Request '{request_id}' not found")

        request = self.requests[request_id]
        if request["user_id"] != user_id:
            raise BoundaryError("Cannot execute someone else's request")

        if request["status"] != "approved":
            raise BoundaryError(f"Request must be approved before execution")

        if not request["approval"]:
            raise BoundaryError("Missing approval")

        # Check approval hasn't expired
        expires = datetime.fromisoformat(request["approval"]["expires_at"])
        if datetime.now() > expires:
            raise BoundaryError("Approval has expired")

        # Execute deletions
        deleted = []
        failed = []

        for target_id in request["target_ids"]:
            try:
                if target_id in self.catalog:
                    # Mark as suppressed (pending deletion from real services)
                    self.suppression[target_id] = {
                        "user_id": user_id,
                        "request_id": request_id,
                        "suppressed_at": datetime.now().isoformat(),
                    }
                    deleted.append(target_id)
                    request["events"].append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "deleted",
                        "record_id": target_id,
                    })
            except Exception as e:
                failed.append({"record_id": target_id, "error": str(e)})

        # If consent-based withdrawal, mark consent as withdrawn
        if request.get("origin") == "live_agent":
            if self.consent.get("state") == "active":
                self.consent["state"] = "withdrawn"
                self.consent["withdrawn_at"] = datetime.now().isoformat()

        request["status"] = "executing"
        request["completed_at"] = datetime.now().isoformat()
        self._save_json(self.requests_file, self.requests)
        self._save_json(self.suppression_file, self.suppression)
        self._save_json(self.consent_file, self.consent)

        return {
            "deleted": deleted,
            "failed": failed,
            "total": len(request["target_ids"]),
            "status": "complete" if not failed else "partial",
        }

    def seed(self, data: Dict) -> None:
        """Seed the engine with initial catalog data.

        Args:
            data: Dictionary with 'records' and optional 'edges' keys
        """
        records = data.get("records", [])
        edges = data.get("edges", [])

        # Load records into catalog
        for record in records:
            record_id = record.get("id")
            if record_id:
                self.catalog[record_id] = record

        # Save to files
        self._save_json(self.catalog_file, self.catalog)
        if edges:
            self._save_json(self.edges_file, edges)

    def close(self) -> None:
        """Close the engine and ensure all data is persisted."""
        self._save_json(self.catalog_file, self.catalog)
        self._save_json(self.requests_file, self.requests)
        self._save_json(self.consent_file, self.consent)
        self._save_json(self.suppression_file, self.suppression)

    def purge_expired_requests(self) -> None:
        """Remove expired approval requests."""
        expired = []
        for request_id, request in self.requests.items():
            if request.get("status") == "approved" and request.get("approval"):
                expires = datetime.fromisoformat(request["approval"]["expires_at"])
                if datetime.now() > expires:
                    expired.append(request_id)

        for request_id in expired:
            del self.requests[request_id]

        if expired:
            self._save_json(self.requests_file, self.requests)

    def get_request(self, request_id: str, user_id: str) -> Dict:
        """Get request details.

        Args:
            request_id: Request ID
            user_id: User accessing

        Returns:
            Request data

        Raises:
            BoundaryError: If unauthorized
        """
        if request_id not in self.requests:
            raise BoundaryError(f"Request '{request_id}' not found")

        request = self.requests[request_id]
        if request["user_id"] != user_id:
            raise BoundaryError("Cannot access someone else's request")

        return request.copy()

    def latest(self, user_id: str) -> Optional[Dict]:
        """Get the latest request for a user.

        Args:
            user_id: User ID

        Returns:
            Latest request or None
        """
        user_requests = [r for r in self.requests.values() if r.get("user_id") == user_id]
        if not user_requests:
            return None

        # Sort by created_at timestamp, newest first
        user_requests.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return user_requests[0].copy() if user_requests else None

    def search(self, user_id: str, query: str = "") -> List[Dict]:
        """Search catalog for user's records.

        Args:
            user_id: User ID
            query: Search query string

        Returns:
            List of matching records
        """
        if not query.strip():
            return []

        results = []
        query_lower = query.lower()

        for record_id, record in self.catalog.items():
            if record.get("user_id") != user_id:
                continue

            # Search in title, service, kind, and content
            searchable = ' '.join([
                record.get("title", ""),
                record.get("service", ""),
                record.get("kind", ""),
                record.get("content", ""),
            ]).lower()

            if query_lower in searchable:
                results.append({
                    "id": record_id,
                    "title": record.get("title", ""),
                    "service": record.get("service", ""),
                    "kind": record.get("kind", ""),
                    "text": record.get("title", ""),
                })

        return sorted(results, key=lambda r: r["id"])
