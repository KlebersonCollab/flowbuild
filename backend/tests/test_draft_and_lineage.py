import pytest
from backend.app.db import DatabaseManager


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_draft.db"
    mgr = DatabaseManager(database_url=f"sqlite:///{db_file}")
    mgr.init_db()
    yield mgr
    mgr.close()


def test_flow_draft_lifecycle(test_db: DatabaseManager):
    flow_payload = {
        "id": "flow-auto-save-1",
        "name": "Auto Save Workflow",
        "environment": "dev",
        "version": "v1.0.0",
        "folder": "Geral",
        "is_draft": True,
        "nodes": [{"id": "n1", "type": "ManualTriggerComponent", "position": {"x": 10, "y": 20}}],
        "edges": [],
    }

    # 1. Auto-save in draft state (is_active=False, is_draft=True)
    rec = test_db.create_flow(flow_payload, is_active=False, is_draft=True)
    assert rec.id == "flow-auto-save-1"
    assert rec.version == "v1.0.0"
    assert rec.is_active is False
    assert rec.is_draft is True

    # 2. Querying active flows excludes in-progress drafts
    active_flows = test_db.list_flows(active_only=True)
    assert not any(f.id == "flow-auto-save-1" for f in active_flows)

    # 3. Explicit save bumps version to v1.0.1 and clears draft
    flow_payload["version"] = "v1.0.1"
    flow_payload["is_draft"] = False
    updated = test_db.create_flow(flow_payload, is_active=True, is_draft=False)
    assert updated.version == "v1.0.1"
    assert updated.is_active is True
    assert updated.is_draft is False

    # 4. Now included in active flows
    active_now = test_db.list_flows(active_only=True)
    assert any(f.id == "flow-auto-save-1" for f in active_now)


def test_promotion_and_dev_deduplication(test_db: DatabaseManager):
    dev_flow = {
        "id": "flow-pipeline-core",
        "name": "Core Pipeline",
        "environment": "dev",
        "version": "v1.0.0",
        "nodes": [],
        "edges": [],
    }
    test_db.create_flow(dev_flow, is_active=True, is_draft=False)

    # Promote to QA
    qa_rec = test_db.promote_flow("flow-pipeline-core", "qa", target_version="v1.1.0")
    assert qa_rec is not None
    assert qa_rec.environment == "qa"
    assert qa_rec.version == "v1.1.0"
    assert qa_rec.source_flow_id == "flow-pipeline-core"
    assert qa_rec.id == "flow-pipeline-core-qa"

    # Promoting again idempotently updates existing QA record rather than multiplying
    qa_rec2 = test_db.promote_flow("flow-pipeline-core", "qa", target_version="v1.1.1")
    assert qa_rec2.id == "flow-pipeline-core-qa"
    assert qa_rec2.version == "v1.1.1"

    # Total QA flows for this source is still 1
    qa_flows = test_db.list_flows(environment="qa")
    assert len(qa_flows) == 1
    assert qa_flows[0].id == "flow-pipeline-core-qa"

    # DEV flows for this source is still 1
    dev_flows = test_db.list_flows(environment="dev")
    assert len(dev_flows) == 1
    assert dev_flows[0].id == "flow-pipeline-core"
