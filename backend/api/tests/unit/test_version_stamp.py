"""Guards that the release version is stamped identically everywhere.

scripts/update-version.sh writes the release number into five files during
semantic-release's prepare step, and @semantic-release/git commits all five in
one commit that the tag then points at. Two of those five are load-bearing at
runtime and are read by DIFFERENT halves of the app:

    backend/api/fixtures/version.json  -> loaded into the DB at container start,
                                          served by /api/v2/version/list
    frontend/package.json              -> inlined into the Vue bundle at build

App.vue compares them and shows a "refresh to update" banner when they differ.
So if a stamp ever lands on one and not the other, every user gets a refresh
prompt that refreshing cannot clear -- and nothing else in the system notices,
because each half is internally valid.

The stamp script asserts each substitution took effect, which catches a pattern
that has drifted. This catches the case that check cannot: a target being
REMOVED from the script (or a file being hand-edited), leaving the remaining
stamps agreeing with each other and one file silently behind.

Deliberately compares the files only to each other, never to a git tag. Between
releases the working tree legitimately carries the LAST release's number on
every branch, so tag-matching would fail on every feature branch.
"""

import json
import re
from pathlib import Path

import pytest


def _repo_root():
    """Walk up for .releaserc.json, which defines the stamping being checked.

    Returns None inside the built image and the dev container, where only
    backend/ is present. CI runs from a full checkout, which is where this
    needs to run.
    """
    for parent in Path(__file__).resolve().parents:
        if (parent / ".releaserc.json").is_file():
            return parent
    return None


ROOT = _repo_root()

pytestmark = pytest.mark.skipif(
    ROOT is None,
    reason="not a full checkout (no .releaserc.json above backend/) -- "
    "only backend/ is present in the image and the dev container",
)

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def _fixture_entry():
    records = json.loads((ROOT / "backend/api/fixtures/version.json").read_text())
    assert len(records) == 1, "the version fixture must hold exactly one record"
    return records[0]


def _stamped_versions():
    """Every stamped version, keyed by the path update-version.sh writes it to."""
    return {
        "backend/api/fixtures/version.json": _fixture_entry()["fields"][
            "version_number"
        ],
        "frontend/package.json": json.loads(
            (ROOT / "frontend/package.json").read_text()
        )["version"],
        "backend/backend/api.py": re.search(
            r'^api\.version = "([^"]*)"',
            (ROOT / "backend/backend/api.py").read_text(),
            re.M,
        ).group(1),
        "scripts/version.txt": (ROOT / "scripts/version.txt").read_text().strip(),
        "Dockerfile": re.search(
            r'^LABEL version="([^"]*)"',
            (ROOT / "Dockerfile").read_text(),
            re.M,
        ).group(1),
    }


@pytest.mark.unit
def test_every_stamped_file_agrees():
    """The five stamp targets must all carry the same version."""
    versions = _stamped_versions()

    assert len(set(versions.values())) == 1, (
        "stamped versions disagree -- the frontend and backend halves of a "
        "release would report different versions and prompt every user to "
        "refresh forever:\n"
        + "\n".join(f"  {path}: {ver}" for path, ver in sorted(versions.items()))
    )


@pytest.mark.unit
def test_stamped_version_is_semver():
    """A malformed stamp means a sed pattern matched something unintended."""
    for path, ver in _stamped_versions().items():
        assert SEMVER.match(ver), f"{path} carries a non-semver version: {ver!r}"


@pytest.mark.unit
def test_stamped_version_fits_the_model_field():
    """Version.version_number is varchar(20); a longer stamp fails at loaddata.

    Which, on Postgres, fails at container start -- the exact failure the
    startup guard in start.app.sh now refuses to boot through.
    """
    from api.models import Version

    max_length = Version._meta.get_field("version_number").max_length
    version = _stamped_versions()["backend/api/fixtures/version.json"]

    assert len(version) <= max_length, (
        f"version {version!r} is {len(version)} chars but version_number holds "
        f"{max_length} -- loaddata will fail and the container will not start"
    )


@pytest.mark.unit
def test_fixture_primary_key_is_one():
    """Both version endpoints look the row up by hardcoded id=1.

    /version/list uses get_object_or_404(Version, id=1), so a fixture written
    to any other pk 404s -- and that endpoint is also the container
    healthcheck, so the image would never report healthy.
    """
    assert _fixture_entry()["pk"] == 1
