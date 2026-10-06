import pytest
import tempfile
import os
from backend.app.db import DatabaseManager

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite:///{path}"
    db = DatabaseManager(database_url=db_url)
    db.init_db()
    yield db
    db.close()
    if os.path.exists(path):
        os.remove(path)

def test_variables_crud_and_scoping(temp_db):
    # 1. Create Global Variable
    global_var = temp_db.create_variable(
        key="BASE_URL",
        value="https://api.global.com",
        scope="global"
    )
    assert global_var.key == "BASE_URL"
    assert global_var.value == "https://api.global.com"
    assert global_var.scope == "global"

    # 2. Create Flow-Scoped Variable
    flow_var = temp_db.create_variable(
        key="BASE_URL",
        value="https://api.flow-special.com",
        scope="flow",
        flow_id="flow-123"
    )
    assert flow_var.key == "BASE_URL"
    assert flow_var.scope == "flow"
    assert flow_var.flow_id == "flow-123"

    # 3. Hierarchy resolution test:
    # In flow-123, BASE_URL resolves to flow value
    val_in_flow = temp_db.resolve_variable_value("BASE_URL", flow_id="flow-123")
    assert val_in_flow == "https://api.flow-special.com"

    # In other flow or global context, BASE_URL resolves to global value
    val_in_other = temp_db.resolve_variable_value("BASE_URL", flow_id="flow-999")
    assert val_in_other == "https://api.global.com"

    # 4. List variables
    all_vars = temp_db.list_variables()
    assert len(all_vars) == 2

    globals_only = temp_db.list_variables(scope="global")
    assert len(globals_only) == 1
    assert globals_only[0].key == "BASE_URL"

    flow_vars = temp_db.list_variables(flow_id="flow-123")
    assert len(flow_vars) == 2  # includes both flow-123 and global variables

    # 5. Update Variable
    updated = temp_db.update_variable(global_var.id, value="https://api.updated-global.com")
    assert updated.value == "https://api.updated-global.com"

    # 6. Delete Variable
    deleted = temp_db.delete_variable(flow_var.id)
    assert deleted is True
    # Now in flow-123, it falls back to global value
    val_after_delete = temp_db.resolve_variable_value("BASE_URL", flow_id="flow-123")
    assert val_after_delete == "https://api.updated-global.com"
