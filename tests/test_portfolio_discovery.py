import pytest

from autohub.models import AutoHubError
from autohub.portfolio import MAX_PORTFOLIO_FILES, discover_workflow_files


def test_shallow_discovery_is_sorted_and_json_only(tmp_path):
    (tmp_path / "b.json").write_text("{}", encoding="utf-8")
    (tmp_path / "a.JSON").write_text("{}", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("private", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "c.json").write_text("{}", encoding="utf-8")

    paths = discover_workflow_files(tmp_path)
    assert [path.name for path in paths] == ["a.JSON", "b.json"]


def test_recursive_discovery_includes_nested_files_in_stable_order(tmp_path):
    (tmp_path / "root.json").write_text("{}", encoding="utf-8")
    nested = tmp_path / "z-folder"
    nested.mkdir()
    (nested / "nested.json").write_text("{}", encoding="utf-8")

    paths = discover_workflow_files(tmp_path, recursive=True)
    assert [path.relative_to(tmp_path).as_posix() for path in paths] == [
        "root.json",
        "z-folder/nested.json",
    ]


def test_discovery_skips_linked_files_and_directories(tmp_path):
    source = tmp_path / "source.json"
    source.write_text("{}", encoding="utf-8")
    linked_file = tmp_path / "linked.json"
    linked_file.symlink_to(source)

    private = tmp_path / "private"
    private.mkdir()
    (private / "hidden.json").write_text("{}", encoding="utf-8")
    linked_directory = tmp_path / "linked-directory"
    linked_directory.symlink_to(private, target_is_directory=True)

    paths = discover_workflow_files(tmp_path, recursive=True)
    relative = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert relative == ["private/hidden.json", "source.json"]
    assert "linked.json" not in relative
    assert all(not value.startswith("linked-directory/") for value in relative)


def test_discovery_rejects_linked_or_non_directory_roots(tmp_path):
    directory = tmp_path / "workflows"
    directory.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(directory, target_is_directory=True)
    with pytest.raises(AutoHubError, match="symbolic link"):
        discover_workflow_files(linked)

    file_path = tmp_path / "workflow.json"
    file_path.write_text("{}", encoding="utf-8")
    with pytest.raises(AutoHubError, match="directory"):
        discover_workflow_files(file_path)


@pytest.mark.parametrize("limit", [0, True, MAX_PORTFOLIO_FILES + 1])
def test_discovery_validates_file_limit(limit, tmp_path):
    with pytest.raises(AutoHubError, match="max_files"):
        discover_workflow_files(tmp_path, max_files=limit)


def test_discovery_rejects_folders_above_explicit_limit(tmp_path):
    for index in range(3):
        (tmp_path / f"{index}.json").write_text("{}", encoding="utf-8")
    with pytest.raises(AutoHubError, match="more than"):
        discover_workflow_files(tmp_path, max_files=2)
