from src.idempotency_store import IdempotencyStore


def test_idempotency_store_survives_new_instance(tmp_path):
    database = tmp_path / "idempotency.sqlite3"
    first = IdempotencyStore(str(database))
    first.put("request-1", {"id": "event-1"})

    second = IdempotencyStore(str(database))

    assert second.get("request-1") == {"id": "event-1"}
    assert second.get("missing") is None
