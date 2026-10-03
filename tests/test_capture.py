"""Offline tests for capture-ledger matching logic."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import capture_ledger  # noqa: E402
import file_transcripts  # noqa: E402
import pending_work  # noqa: E402


def test_norm_name_ignores_copy_suffix_case_and_punctuation():
    assert capture_ledger.norm_name("syllabus - Copy (1).html") == capture_ledger.norm_name("Syllabus.html")
    assert capture_ledger.norm_name("AI5100-week4-lecture-live.pdf") == "ai5100week4lecturelive"


def test_loose_name_matches_chrome_duplicate_downloads():
    assert file_transcripts.loose_name("AI5100-week6-lecture-live (1).pdf") == file_transcripts.loose_name("AI5100-week6-lecture-live.pdf")
    assert file_transcripts.loose_name("a.pdf") != file_transcripts.loose_name("a.html")


def test_private_links_never_synced_to_public_readings():
    for url in ("https://vanderbilt.zoom.us/rec/share/x", "https://vanderbilt.box.com/s/abc", "https://brightspace.vanderbilt.edu/d2l/x"):
        assert any(h in url for h in capture_ledger.PRIVATE_HOSTS)


def test_bucket_routing():
    b = pending_work.bucket_of
    assert b({"stage": "posted", "next_action": "download `x.pdf` from Brightspace"}) == "download"
    assert b({"stage": "acquired", "next_action": "convert: convert_content.py --week 3"}) == "convert"
    assert b({"stage": "converted", "next_action": "lecture notes from `x.vtt`"}) == "notes"
    assert b({"stage": "converted", "next_action": "summarize paper -> wiki/sources/x.md"}) == "summarize"
    assert b({"stage": "digested", "next_action": "reference in lectures/Week-03.md"}) == "integrate"
    assert b({"stage": "tracked", "next_action": "check homework-queue.md"}) is None
    assert b({"stage": "integrated", "next_action": ""}) is None


def test_session_kind_by_speaker_count():
    live = "1\n00:00:01.000 --> 00:00:02.000\nAmy: hi\n\n2\nRich: hello\n\n3\nTim: welcome\n"
    solo = "1\n00:00:01.000 --> 00:00:02.000\nTim Darrah: today we cover\n"
    assert file_transcripts.session_kind(live) == "live"
    assert file_transcripts.session_kind(solo) == "async"
