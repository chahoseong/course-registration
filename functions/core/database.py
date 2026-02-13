import os

import firebase_admin
from google.cloud import firestore as google_firestore


DEFAULT_DB_CANDIDATES = ["course-registration", "(default)"]


def _build_client(project_id: str, db_id: str):
    if db_id == "(default)":
        return google_firestore.Client(project=project_id)
    return google_firestore.Client(project=project_id, database=db_id)


def _resolve_db_candidates() -> list[str]:
    explicit = (os.getenv("FIREBASE_DATABASE_ID") or "").strip()
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    for db_id in DEFAULT_DB_CANDIDATES:
        if db_id not in candidates:
            candidates.append(db_id)
    return candidates


def _has_seed_data(client) -> bool:
    for collection_name in ("users", "courses"):
        docs = list(client.collection(collection_name).limit(1).stream())
        if docs:
            return True
    return False


def get_db():
    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    project_id = (
        os.getenv("GCLOUD_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or "course-registration-711a4"
    )

    explicit = (os.getenv("FIREBASE_DATABASE_ID") or "").strip()
    candidates = _resolve_db_candidates()
    last_error = None
    connected: list[tuple[str, object]] = []

    for db_id in candidates:
        try:
            client = _build_client(project_id, db_id)
            # Trigger a lightweight RPC so missing DB fails fast.
            next(client.collections(), None)
            connected.append((db_id, client))
            if explicit:
                print(f"[database] Connected to Firestore DB (explicit): {db_id}")
                return client
        except Exception as e:
            last_error = e
            print(f"[database] Failed to connect DB '{db_id}': {e}")

    for db_id, client in connected:
        try:
            if _has_seed_data(client):
                print(f"[database] Connected to Firestore DB (auto-data): {db_id}")
                return client
        except Exception as e:
            last_error = e
            print(f"[database] Data probe failed for DB '{db_id}': {e}")

    if connected:
        db_id, client = connected[0]
        print(f"[database] Connected to Firestore DB (auto-fallback): {db_id}")
        return client

    raise RuntimeError(
        f"Unable to connect to Firestore databases {candidates}: {last_error}"
    )
