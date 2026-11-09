"""Snapshot tests: one small, made-up post per feature of the renderer.

Each ``snapshots/<feature>.html`` is a post's HTML as a feed would deliver it,
and ``snapshots/<feature>.expected.html`` is what ``render_chapter`` makes of
it. When a test fails, its name says which feature changed.

After an intended change, regenerate the expected files and review the diff:

    pytest tests/test_snapshots.py --update-snapshots
"""

from pathlib import Path

import pytest

from feedpaper.client import Article
from feedpaper.render import render_chapter

SNAPSHOTS = Path(__file__).parent / "snapshots"
FEATURES = sorted(
    path.stem for path in SNAPSHOTS.glob("*.html") if ".expected" not in path.suffixes
)

# Where the downloaded images end up in the book. Any other image counts as a
# failed download, so render_chapter drops it.
IMAGES = {
    "https://images.example/photo.jpg": "images/img_1.jpg",
    "https://images.example/chart.png": "images/img_2.png",
}


@pytest.mark.parametrize("feature", FEATURES)
def test_snapshot(feature, update_snapshots):
    source = (SNAPSHOTS / f"{feature}.html").read_text(encoding="utf-8")
    expected_path = SNAPSHOTS / f"{feature}.expected.html"

    article = Article(id="1", title=feature, html=source, feed_title="")
    rendered = render_chapter(article, IMAGES) + "\n"

    if update_snapshots or not expected_path.exists():
        expected_path.write_text(rendered, encoding="utf-8")
        if not update_snapshots:
            pytest.fail(f"Wrote missing snapshot {expected_path.name}; review it.")
    assert rendered == expected_path.read_text(encoding="utf-8")


def test_every_feature_has_a_snapshot():
    expected = {path.name.removesuffix(".expected.html") for path in SNAPSHOTS.glob("*.expected.html")}

    assert expected == set(FEATURES)
