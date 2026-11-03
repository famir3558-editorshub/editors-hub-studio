# Data formats

## Library folder (`@@LIBRARY_DIR@@`)

The CLI finds it from `$BROLL_LIBRARY`, else the setup answer `library_dir` in the creator profile, else
`~/BrollLibrary`.

```
BrollLibrary/
  library.db        SQLite: the index (source of truth for metadata)
  concepts.json     concept -> visual terms used to widen searches (editable)
  frames/<clip_id>/ sampled frames + contact sheets (safe to delete; re-made by extract)
  pending/          analysis templates waiting to be filled and ingested
  plans/            B-roll placement plans per video
  exports/          FCP7 XML, Premiere JSX and CSV files
  backups/          JSON snapshots from `broll backup`
```

The media files stay where they are and remain the source of truth. The database only points to
them (`root` + relative path), so a drive mounted somewhere new only needs `relink`.

## Identity, duplicates and incremental updates

- `quick_hash` = SHA-256 of file size + the first, middle and last 1 MB. Fast on huge files and
  stable across renames and moves.
- Clip `id` = `c_` + first 12 hex of that hash, assigned once and never changed.
- On `scan`, per file: same path + same size + same mtime -> unchanged (not even hashed).
  Same path, different hash -> `changed`, analysis cleared, back to pending.
  New path whose hash matches a clip whose old path is gone -> `moved`, analysis kept.
  New path whose hash matches a clip that still exists -> `duplicate` (linked via `duplicate_of`,
  excluded from search). Registered path that disappeared -> `missing` (kept; restored when it
  reappears).

Status lifecycle: `pending -> analyzed`; `analyzed -> pending` (content changed);
`any -> missing -> analyzed/pending` (file returns); `error` (ffprobe/frame failure).

## Analysis record (stored in `clips.analysis`)

Required: `summary, description, activity, shot_type, camera_movement, speaking,
tags_literal (>=5), tags_conceptual (>=5), editorial_uses (>=2), segments (>=1), best_section,
quality (1-5), usefulness (1-5)`.

Optional: `people, location, environment, time_of_day, setting_details, objects, devices,
actions, camera_angle, subject_movement, lighting, colour, mood, avoid_for, issues, notes`.

```json
{
  "clip_id": "c_39cdd491d2c2",
  "summary": "string",
  "description": "string",
  "people": ["@@CREATOR_FIRST_NAME@@ (subject, upper body)"],
  "speaking": "none | talking to camera | talking off camera | on a call | background voices",
  "location": "string", "environment": "indoor | outdoor | vehicle | screen", "time_of_day": "string",
  "setting_details": "string",
  "objects": ["string"], "devices": ["string"],
  "activity": "string", "actions": ["string"],
  "shot_type": "string", "camera_angle": "string", "camera_movement": "string", "subject_movement": "string",
  "lighting": "string", "colour": "string", "mood": ["string"],
  "tags_literal": ["lowercase"], "tags_conceptual": ["lowercase"],
  "editorial_uses": ["string"], "avoid_for": ["string"],
  "segments": [{"start": 0.0, "end": 1.5, "description": "string", "usable": false, "quality": 1}],
  "best_section": {"start": 3.0, "end": 9.0, "why": "string"},
  "quality": 4, "usefulness": 5,
  "issues": ["string"], "notes": "string"
}
```

Technical metadata (duration, resolution, fps, codec, orientation, rotation, audio channels,
creation time, audio profile) comes from ffprobe/ffmpeg and is stored in its own columns.

## Plan (`plans/<project>.json`)

```json
{
  "project": "Episode 4 working title",
  "main_video": "/path/to/edits/episode_4_main.mp4",
  "fps": 25, "width": 1920, "height": 1080,
  "transcript": "/path/to/captions.srt",
  "placements": [
    {
      "n": 1,
      "at": 42.4,
      "duration": 3.2,
      "clip_id": "c_39cdd491d2c2",
      "src_in": 3.5,
      "track": 2,
      "says": "Building a business requires a lot of focused work.",
      "visual_idea": "the creator working at the desk",
      "why": "literal focused work at their own desk",
      "alternatives": ["c_ab12cd34ef56"]
    }
  ],
  "gaps": [
    {"at": 95.0, "says": "my phone was blowing up with DMs", "visual_idea": "phone screen with notifications", "suggest": "film new: close-up of phone lighting up"}
  ]
}
```

- `at` = seconds on the main video's timeline; `src_in` = seconds into the B-roll clip;
  `duration` = seconds on screen. `track` defaults to 2 (V2).
- `main_video` is optional; with it the XML includes the talking-head on V1/A1.

## Database tables

`clips` (one row per file, metadata + analysis JSON + status + use_count), `clips_fts` (FTS5 full
text index over summary, description, activity, tags, uses, objects, environment, mood, shot,
filename; porter stemming), `roots` (registered footage folders), `usage` (which clip was used in
which project, where), `meta` (schema version).

Search ranking = BM25 over weighted fields (tags and activity weigh most), blended 75/25 with
quality + usefulness, optional penalty for heavy past use. Semantic judgement is done by Claude
reranking the candidates; to add vector embeddings later, add an `embeddings` table keyed by clip
id and blend cosine similarity into `cmd_search`.
