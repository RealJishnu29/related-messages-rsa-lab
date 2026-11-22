import json
from pathlib import Path

import pytest

from related_messages import demo_values, load_input, recover_related_message


def test_demo_recovery_returns_harmless_integer():
    values = demo_values()
    assert recover_related_message(**values) == 12_345


def test_wrong_relationship_is_rejected():
    values = demo_values()
    values["c1"] = (values["c1"] + 1) % values["n"]
    with pytest.raises(ValueError):
        recover_related_message(**values)


def test_json_loader_requires_exact_schema(tmp_path: Path):
    path = tmp_path / "sample.json"
    path.write_text(json.dumps({"n": "77", "e": 17, "c1": "1", "c2": "2", "delta": -3}),
                    encoding="utf-8")
    assert load_input(path)["n"] == 77
    path.write_text('{"n":"77","e":17,"c1":"1","c2":"2","delta":-3,"flag":"secret"}',
                    encoding="utf-8")
    with pytest.raises(ValueError):
        load_input(path)
