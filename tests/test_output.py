import os

import pytest

from autohub.models import AutoHubError
from autohub.output import write_output


def test_output_creates_parent_and_private_file(tmp_path):
    destination = tmp_path / "private" / "plan.json"
    assert write_output(destination, "{}\n") == destination
    assert destination.read_text(encoding="utf-8") == "{}\n"
    if os.name == "posix":
        assert destination.stat().st_mode & 0o777 == 0o600


def test_output_never_overwrites_existing_file(tmp_path):
    destination = tmp_path / "plan.json"
    destination.write_text("original", encoding="utf-8")
    with pytest.raises(AutoHubError, match="already exists"):
        write_output(destination, "replacement")
    assert destination.read_text(encoding="utf-8") == "original"


def test_output_rejects_symbolic_link_destination(tmp_path):
    target = tmp_path / "target.json"
    target.write_text("private", encoding="utf-8")
    linked = tmp_path / "linked.json"
    linked.symlink_to(target)
    with pytest.raises(AutoHubError):
        write_output(linked, "replacement")
    assert target.read_text(encoding="utf-8") == "private"
