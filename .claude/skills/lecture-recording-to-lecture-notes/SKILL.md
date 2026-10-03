---
name: lecture-recording-to-lecture-notes
description: Convert lecture recordings (.vtt transcripts, optional .mp4 video and slides) into polished Markdown lecture notes with auto-extracted screenshots, embedded slides, speaker quotes, and Q&A sections. Use for any lecture, class, or talk recording.
---

# Lecture Recording to Lecture Notes

Transform lecture recordings into polished, tutorial-style Markdown notes. Given a transcript (and optionally video, slides, and supplementary materials), produce a complete Markdown document with embedded images — including auto-extracted screenshots from demo moments in the video.

This skill does not transcribe audio. A `.vtt` transcript must already exist.

## Jock's Preferences

These override anything below that conflicts. When Jock gives feedback on a set of notes ("too wordy", "more math", "fewer quotes"), turn it into a rule in this section, tell Jock which line changed, and offer to regenerate the affected section. `SKILL.upstream.md` is the original, untouched copy for comparison.

**Audience.** Jock is a Vanderbilt MS AI student with a business background who is building technical depth. Pitch every section to that reader: assume smart, assume busy, do not assume the math or the jargon.

**Teaching order.** For each concept: intuition first, then the precise version. Define every technical term the first time it appears. Use a business analogy where one genuinely fits, never in place of the precise version.

**Plain-terms callouts.** For each concept that is genuinely hard (math, an algorithm, an architecture), add a short callout right after it:

> **In plain terms:** two to four sentences a smart non-specialist would follow.

For equations, say what each symbol means and what the equation is doing before or after showing it.

**Level of detail.** Complete enough that Jock could study from the notes without rewatching, but cut repetition, tangents, and logistics (breaks, audio checks, homework admin goes in one line at the end under "Course logistics" if any).

**Quiz.** End the notes (after Summary, before References) with `## Check Your Understanding`: 3 to 5 questions that test understanding, not recall of wording. Put each answer in a collapsed block:

<details><summary>Answer</summary>

The answer, with the section it comes from.

</details>

**Wiki links.** Link key terms to the study wiki (see Phase 4).

## MS AI vault overlay

Paths for the Command Center (`C:\Users\jockt\dev\ms_ai`). These override the generic paths below. `AGENTS.md` has the full path table.

| Role | Path |
|------|------|
| Read sources | `C:\Users\jockt\Dropbox\Vandy_MS_AI\Coursework\AI 5100 Week N\` (VTT, slides, optional local mp4) |
| Write notes + images | `C:\Users\jockt\Dropbox\Vandy_MS_AI\Vandy Other\wiki\courses\AI-5100\lecture-notes\week-NN\<YYYY-MM-DD>-<topic-slug>\` |
| Study wiki (Phase 4) | `...\Vandy Other\wiki\concepts\` (concept pages) and `...\wiki\raw\courses\AI-5100\week-NN\` (converted papers) |
| Python | `C:\Users\jockt\dev\ms_ai\.venv\Scripts\python.exe` (there is no `python3` on this machine) |

- Never modify or move files in `Coursework/`. Never write into `wiki/raw/` (settings deny it).
- Never copy `.mp4` into git.
- Zoom VTT is a **gap-fill** source. Granola notes in `Coursework/AI 5100 Week N/sessions/` are primary for live Tuesday sessions; read them as supplementary material when present.
- **Transcript naming.** `python scripts\file_transcripts.py` files Zoom downloads as `Coursework/AI 5100 Week N/transcripts/<YYYY-MM-DD>-<live|async>.transcript.vtt`. Use the date and live/async in the notes folder slug and title. Older VTTs may still sit in the week folder root under their Zoom names.
- **Unattended mode.** When the run was started by a scheduled task or by "process pending transcripts" (the list comes from `python scripts\pending_work.py`), skip the Phase 0 confirmation: record the inventory in the notes' frontmatter, skip video screenshots unless an `.mp4` is already local, never install packages, and process each pending transcript in turn. Always record `source_transcript:` with the exact `.vtt` filename; `pending_work.py` uses it to know which transcripts are done.
- After notes are written, stop. The weekly lecture page `wiki/courses/AI-5100/lectures/Week-NN.md` belongs to **Librarian** session merge; offer the hand-off.

## Workflow

Execute these five phases (0 to 4) in order. After Phase 0, confirm the inventory with the user before proceeding.

---

### Phase 0: Discovery & Prerequisites

**Scan the week folder** (`Coursework\AI 5100 Week N\`, or the folder the user named) and classify all relevant files:

| Type | Extensions | Role |
|------|-----------|------|
| Transcript | `.vtt` | Required — WebVTT from Zoom |
| Video | `.mp4` | Optional — needed for auto-screenshots |
| Slides | `.pptx`, `.pdf` | Optional — embedded in notes |
| Supplementary | `.md`, `.txt`, `.docx`, papers | Optional — extra context |
| Manual screenshots | Images in `screenshots/` | Optional — included alongside auto-extracted |

**Check for required tools and Python packages:**

- `pymupdf` Python package — needed for PDF slide conversion. Check with `python3 -c "import fitz"`. Install with `pip install pymupdf` if missing.
- `opencv-python` Python package — needed for screenshot extraction from video. Check with `python3 -c "import cv2"`. Install with `pip install opencv-python` if missing.
- `python-pptx` Python package — needed for PPTX slide text extraction. Check with `python3 -c "import pptx"`. Install with `pip install python-pptx` if missing. Only needed if PPTX files are present.

**Do not install anything without asking.** List missing packages in the inventory with the exact `pip install` command and let the user decide. The bundled scripts exit with an install hint instead of installing. On Windows, use `python` if `python3` is not found.

**Present inventory to the user:**
```
## Discovered Files
- Transcript: [filename.vtt]
- Video: [filename.mp4] (or "not found")
- Slides: [filename.pptx] (or "not found")
- Supplementary: [list or "none"]
- Manual screenshots: [count] images in screenshots/ (or "none")

## Tool Availability
- pymupdf (Python): [available/installed/missing]
- opencv-python (Python): [available/installed/missing — needed for video screenshots]
- python-pptx (Python): [available/installed/missing — only needed for PPTX slides]
```

**Wait for user confirmation before proceeding.**

If the transcript `.vtt` file is not found, stop and ask the user to provide one.

---

### Phase 1: Slide Deck Conversion

Skip this phase if no slide deck is found.

**Goal:** Convert slides into individual PNG images at `slides/slide-NNN.png`.

**For PDF slides (preferred — Python-based, no external tools needed):**

Use the bundled script (exits with an install hint if `pymupdf` is missing):

```bash
python3 <skill-path>/scripts/pdf_to_slides.py "slides.pdf" slides/
```

**For PPTX slides:**

First check if `libreoffice` is available (`which libreoffice` or `which soffice`). If so, convert to PDF then to PNGs for high-quality slide images:

```bash
libreoffice --headless --convert-to pdf presentation.pptx --outdir .
```
Then use the pymupdf PDF-to-PNG conversion above on the resulting PDF.

If `libreoffice` is not available, use the bundled script to extract structured text from each slide for transcript alignment (auto-installs `python-pptx` if missing):

```bash
python3 <skill-path>/scripts/pptx_to_text.py "presentation.pptx" -o slides_text.json
```

Since `python-pptx` cannot render slides as images, rely on video screenshots to provide visuals for PPTX-based sessions when LibreOffice is unavailable.

**Fallback chain for PDF slides** if `pymupdf` is unavailable:
1. `pdftoppm` (from poppler): `pdftoppm -png -r 200 slides.pdf slides/slide` then rename to zero-padded format
2. ImageMagick `convert`: `convert -density 200 slides.pdf slides/slide-%03d.png`

After conversion, report the number of slides extracted.

---

### Phase 2: Transcript Analysis & Screenshot Extraction

#### 2a. Parse the VTT Transcript

Read the `.vtt` file and parse it into structured entries:
```
{ index, start_time, end_time, speaker, text }
```

VTT format rules:
- Lines with `-->` contain timestamps: `HH:MM:SS.mmm --> HH:MM:SS.mmm`
- Speaker names often appear as `Speaker Name: text` on the text line
- Blank lines separate entries
- Skip the `WEBVTT` header and any `NOTE` blocks

Merge consecutive entries from the same speaker into coherent paragraphs for analysis.

#### 2b. Detect Demo/Screen Moments

Identify timestamps where visual content is important using three methods:

**Method 1 — Regex triggers.** Flag entries containing phrases like:
- "let me show you", "as you can see", "if you look at", "on the screen"
- "I'm clicking", "let me click", "I'll type", "in the terminal", "in the browser"
- "let me share my screen", "let me demonstrate", "here's an example"
- "let me pull up", "switching to", "opening up", "running this"
- "the output shows", "you'll see", "notice that", "look at this"

**Method 2 — Gap detection.** Flag gaps where `start_time(entry N+1) - end_time(entry N) > 3 seconds`. Silent pauses often indicate visual activity (typing, navigating, waiting for output).

**Method 3 — Slide transitions.** Flag phrases indicating slide changes:
- "next slide", "moving on", "let's move to", "the next topic"
- Significant topic shifts detected by comparing adjacent entry content

Collect all flagged timestamps into a deduplicated list.

#### 2c. Extract Frames from Video

Skip if no `.mp4` video is found.

For each detected timestamp, extract a frame with a 2-second offset (to let the screen settle).

**Preferred method — Python with opencv-python (no system dependencies):**

Use the bundled script (auto-installs `opencv-python` if missing). Pass timestamps as a JSON array of seconds:

```bash
python3 <skill-path>/scripts/extract_frames.py "recording.mp4" screenshots/ '[2700, 2850, 3000]'
```

**Fallback — ffmpeg (if opencv-python is unavailable):**
```bash
mkdir -p screenshots
ffmpeg -ss <seconds + 2> -i recording.mp4 -frames:v 1 -q:v 2 screenshots/auto_<timestamp>.png
```

Use the format `auto_HHMMSS.png` for filenames (e.g., `auto_004523.png` for 00:45:23).

**Deduplication:**
- Merge timestamps within 5 seconds of each other (keep the later one)
- After extraction, use Claude's vision capability to compare adjacent screenshots and drop near-identical frames (e.g., same slide with no meaningful change)

**Slide vs. screenshot selection:** When both a slide image and a video screenshot exist for the same moment, do not use both. The goal is one image per moment:
- If the speaker is discussing content that is on a slide, use only the slide image (it will be higher quality than a video capture of the same slide)
- If the video shows something other than the slides (e.g., a live demo, a browser, a terminal, a different application), use the screenshot
- To decide efficiently: use the slide-to-transcript alignment from Phase 2e to find which single slide corresponds to each screenshot's timestamp. Compare the screenshot only against that one aligned slide — not against all slides. If they show the same content, keep only the slide and discard the screenshot

#### 2d. Incorporate Manual Screenshots

If a `screenshots/` folder exists with pre-existing images, include them in the output. Sort manual screenshots by filename and interleave them with auto-extracted screenshots based on best-guess chronological order.

#### 2e. Align Slides to Transcript

If slides were extracted in Phase 1:
1. For each slide image, use Claude's vision to read the slide title and key text
2. Search the transcript for the segment that best matches each slide's content
3. Record the mapping: `slide-NNN.png → transcript segment at timestamp T`

This mapping is used in Phase 3 to place slides at the correct positions in the notes.

---

### Phase 3: Note Generation

Write all outputs into the wiki's lecture-notes folder (see MS AI vault overlay), one folder per lecture:

```
wiki/courses/AI-5100/lecture-notes/week-NN/<YYYY-MM-DD>-<topic-slug>/
  <YYYY-MM-DD>-<topic-slug>.md
  slides/
  screenshots/
```

`week-NN` is the course week from the source folder name. The date is the recording date. Leave the source files (VTT, MP4, slides) where they are; do not move or delete them. Generate `slides/` and `screenshots/` directly into the lecture folder, and put any intermediate files (like `slides_text.json`) there too.

The Markdown file should have this structure:

```markdown
---
title: "[Lecture Title]"
date: "[Date of recording]"
presenter: "[Speaker Name(s)]"
duration: "[Total duration from transcript timestamps]"
source_transcript: "[filename.vtt]"
---

# [Lecture Title]

## Key Concepts and Learning Objectives

**Key Terms and Concepts:**
- Term 1 — definition or explanation
- Term 2 — definition or explanation
- ...

**Learning Objectives:**
1. Understand [concept]...
2. Be able to [skill]...
3. ...

---

## [Section Title]

![Slide: [slide title]](slides/slide-001.png)

Tutorial-style narrative prose that explains the content covered in this
section. This is NOT a raw transcript — it is rewritten as clear, readable
instructional text that follows the lecture's logical flow.

> "Direct quote from the speaker that captures a key insight or memorable
> phrasing" — Speaker Name

More prose explaining the next concept...

### Demo: [What Was Demonstrated]

![Screenshot](screenshots/auto_004523.png)

Step-by-step walkthrough of what's happening on screen. Describe what the
viewer would see: the tool being used, the commands typed, the output
produced, and what it means.

---

## [Next Section Title]

... (repeat pattern) ...

---

## Q&A

**Q (Audience Member Name):** The question asked?

**A (Speaker Name):** The answer given, paraphrased for clarity.

---

## Summary

- Bullet-point summary of the main takeaways from the lecture
- Each point should be actionable or conceptual

## Check Your Understanding

1. A question that tests understanding

<details><summary>Answer</summary>

The answer, and which section covers it.

</details>

## References

- Links, papers, tools, or resources mentioned during the lecture
```

#### Style Rules

1. **Preamble first.** Start with key concepts, terms, and learning objectives before the body. Derive these from the transcript content and any supplementary materials. If supplementary materials include explicit objectives, use those.

2. **Tutorial-style prose.** Rewrite transcript content as clear instructional narrative. Do not dump raw transcript text. Preserve the speaker's logical flow but improve clarity, fix filler words, and add structure.

3. **Speaker quotes as blockquotes.** When the speaker says something particularly insightful, memorable, or important, include it as a blockquote with attribution: `> "quote" — Name`.

4. **Section boundaries.** Create new sections at natural topic transitions. Use slide transitions, explicit "moving on" phrases, and topic shifts as section boundary signals.

5. **Q&A sections.** When audience members ask questions (detected by speaker changes and question phrasing), format them in the Q&A style. Group Q&A at the end or inline with the relevant section — use judgment based on how the lecture flowed.

6. **Image placement.** Place slide images at the start of their corresponding section. Place screenshots inline where the demo or visual moment occurred in the narrative. Never show both a slide and a screenshot for the same moment — if the video frame just shows the slide, use only the slide image.

7. **Relative paths.** All image paths must be relative to the output Markdown file (e.g., `slides/slide-001.png`, `screenshots/auto_004523.png`).

8. **Metadata frontmatter.** Include YAML frontmatter with title, date, presenter, duration, and source transcript filename.

9. **No hallucinated content.** Only include information that appears in the transcript, slides, or supplementary materials. Do not invent examples, add external references not mentioned, or fabricate speaker quotes. The exceptions are the teaching aids from Jock's Preferences (term definitions, plain-terms callouts, analogies, quiz questions): these may explain in your own words, but must not add facts the lecture did not state. If a definition or explanation goes beyond the lecture, mark it *(added for clarity)*.

---

### Phase 4: Link to the Study Wiki

1. For each key term and concept in the notes, check `wiki/concepts/` for an existing concept page (match on filename and on the page title, allowing for plurals and abbreviations like "RLHF").
2. On the first mention in the notes body, link matches as `[[concept]]`. Do not link the same term twice.
3. If a lecture concept matches a converted paper in `wiki/raw/courses/AI-5100/week-NN/`, mention it where relevant (e.g., "see [[2017-06-vaswani-attention-is-all-you-need]]").
4. Do not create or edit `wiki/` pages in this skill. Report back:
   - the terms linked to existing pages
   - the important concepts with no wiki page, and offer to create them
   - anything the lecture says that contradicts an existing wiki page, quoting both

---

## Important Notes

- **Large transcripts**: For transcripts longer than ~50,000 tokens, process in chunks by time range (e.g., 15-minute segments) and stitch together at the end.
- **Multiple speakers**: Track speaker names throughout and attribute quotes correctly. If the VTT doesn't include speaker names, ask the user to identify speakers.
- **Speaker name verification**: VTT transcripts from Zoom often misidentify speakers. Cross-reference speaker names against slide deck title slides, which typically show the actual presenter name and affiliation. When the slides and the VTT conflict, prefer the slides. If the user named the presenter, use that name and mention the conflict.
- **Output location**: `wiki/courses/AI-5100/lecture-notes/week-NN/<YYYY-MM-DD>-<topic-slug>/` (see MS AI vault overlay and Phase 3).
- **Iterative refinement**: After generating the first draft, offer to refine specific sections, add more screenshots, or adjust the level of detail.
