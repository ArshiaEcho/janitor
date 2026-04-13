# Markdown link audit patterns

Load this file when janitor-claude needs to audit wiki-links and markdown links inside a directory. This file is the source of truth for the regex patterns, resolution rules, and reporting format.

**The single most important rule in this file: never auto-rewrite a broken link.** Always report with options, let the user decide. Forward-linking (pointing at a page that doesn't exist yet) is a legitimate Obsidian pattern — the user may be intentionally linking to something they haven't written yet.

---

## Mode detection

Before auditing, decide which mode to run in:

- **Obsidian vault mode** — triggered if any of these exist at the repo root (or any parent up to the filesystem root): `.obsidian/`, `.obsidian.vimrc`, a `templates/` folder next to many `.md` files, dataview-style front-matter. Use the vault-aware resolution rules below.
- **Generic markdown mode** — no Obsidian markers. Treat links as plain filesystem paths relative to the source file.

If both could apply, prefer Obsidian mode when there's a `.obsidian/` directory, generic mode otherwise.

---

## Pattern set

### Obsidian wiki-links

The full Obsidian wiki-link grammar is:

```
[[Target Page]]
[[Target Page|Alias text]]
[[Target Page#Heading]]
[[Target Page#Heading|Alias]]
[[Target Page^block-id]]
[[folder/Target Page]]
![[Target Page]]          ← embed
![[image.png]]            ← image embed
```

Regex (PCRE, multiline off):

```
\[\[([^\[\]\|#\^]+?)(?:#([^\[\]\|\^]+?))?(?:\^([^\[\]\|]+?))?(?:\|([^\[\]]+?))?\]\]
```

Capture groups:
1. Target (page name or path)
2. Heading (optional)
3. Block ID (optional)
4. Alias (optional)

**Embeds** (`![[...]]`) use the same grammar, just with a leading `!`. Treat them the same way — a broken embed is still a broken link.

### Generic markdown links to local files

```
\[([^\[\]]+)\]\(((?!https?://|mailto:|#)[^)\s]+?\.(?:md|markdown|mdx))(?:\s+"[^"]*")?\)
```

This captures `[text](path/to/file.md)` or `[text](./path/to/file.md "title")`, ignoring URLs and anchor-only links. Adjust the extension set if the project uses `.mdx`.

---

## Resolution rules — Obsidian mode

Obsidian resolves wiki-links by **basename**, not by path. `[[My Note]]` resolves to the file `My Note.md` *anywhere* in the vault, as long as the basename is unique. This is non-obvious and users often don't realize it.

### Step 1 — build a basename index

Walk the vault once and build a map from basename (without extension) to full path:

```
basename_index = {
  "My Note": ["areas/ideas/My Note.md"],
  "Project X": ["projects/Project X.md"],
  "Duplicate": ["areas/Duplicate.md", "archive/Duplicate.md"],
  ...
}
```

**Exclude** `.obsidian/`, `.trash/`, `.git/` and any folder the user has set to "exclude from search" in their Obsidian config (not readable from outside Obsidian, so this is best-effort).

### Step 2 — resolve each link

For `[[Target]]`:

1. **Exact basename match** in the index → resolved. If multiple hits (the "Duplicate" case), it's ambiguous — report it even though it's not technically broken.
2. **Path-like target** (contains `/`): resolve as a relative path first from the vault root, then from the source file's folder. If that path exists as `.md`, resolved.
3. **Case-insensitive fallback**: some users type `[[my note]]` instead of `[[My Note]]`. Try the case-insensitive match. If it hits, the link *works* in Obsidian (Obsidian is case-insensitive on case-insensitive filesystems) — don't report as broken, but optionally note the case mismatch.
4. **No match** → broken.

### Step 3 — validate headings and block IDs

If the link specifies `#Heading`:
- Open the target file, extract all headings (`^#+ (.*)$`).
- If the heading doesn't exist, report as "target exists, heading missing." These are soft broken — still functional in Obsidian, just imperfect.

If the link specifies `^block-id`:
- Search the target file for `^block-id$` at end of a line.
- Same soft-broken handling if not found.

---

## Resolution rules — generic markdown mode

Much simpler. Every link is a filesystem path relative to the source file's directory.

For `[text](relative/path.md)` from source file `src/docs/intro.md`:
1. Construct the absolute path: `src/docs/relative/path.md`
2. Check if the file exists.
3. If it doesn't, broken.

Anchor fragments (`#heading`) work the same way as Obsidian — check if the heading exists in the target.

---

## Fuzzy match suggestions

When a link is broken, offer a "did you mean" suggestion if there's a close match. Use a conservative similarity threshold:

- Minimum similarity: **85%** (Levenshtein-based ratio, or equivalent).
- Maximum suggestions per broken link: **1**. Don't offer a list — that's friction without clarity.
- Only suggest if there's exactly one candidate above threshold. If two candidates are both above 85%, show neither and flag as ambiguous.

Algorithm:
1. Take the broken target basename.
2. Compute similarity against every basename in the index.
3. Keep candidates above 0.85.
4. If exactly one survives, that's the suggestion.
5. If zero or multiple, no suggestion.

**Do not use embeddings, LLM similarity, or anything that makes a network call.** String distance only, offline.

---

## Reporting format

Broken links are reported **grouped by source file**, in this format:

```
### docs/design-notes.md

Line 42: [[API Overview]]
  → Not found. Did you mean: [[API Overview v2]]?  (similarity 0.91)
  Options: [1] ignore  [2] fix to suggested  [3] remove link  [4] skip file

Line 108: [[Deprecated Patterns]]
  → Not found. No close match.
  Options: [1] ignore  [2] remove link  [3] skip file
```

**Never do any of these**:

- **Never batch-apply a fix across multiple links** without showing each one and getting per-link confirmation. "Fix all the broken links" is the kind of thing that eats half a vault silently.
- **Never auto-rewrite.** Even if the suggestion is 99% similarity, the user makes the final call. Every fix is a three-option menu: ignore, fix, remove.
- **Never follow option [2] (fix to suggested) for more than one link without re-asking.** Re-ask every time. This is slow but it's the only way to keep the user in control.
- **Never delete the source file** because it has broken links. That's a different question entirely and it is not janitor's decision to make.

---

## Performance / scale rules

On large vaults (1,000+ markdown files) the naive O(n·m) broken-link scan can be slow. Keep the scan fast by:

1. **Building the basename index once**, upfront, rather than re-globbing for each link.
2. **Skipping excluded directories** at walk time, not filter time. Use `find . -type d \( -name .git -o -name .obsidian -o -name node_modules \) -prune -o -type f -name "*.md" -print`.
3. **Batching reads**: read each `.md` file exactly once, extract all links in one pass, rather than re-reading for each link.
4. **Capping at ~2,000 links reported** in a single run. If there are more, report the first 2,000 and tell the user "there are N more broken links; re-run after resolving these." This is not a limitation, it's a signal that the vault needs a sustained cleanup pass, not a single mega-fix.

---

## Things the user will say that sound like "fix all the broken links" but aren't

These phrases come up and janitor must not over-interpret them:

- **"Clean up my broken links"** → report them grouped, ask per-link.
- **"I have a bunch of broken wiki-links"** → same. Report first, act second.
- **"Fix the links in this file"** → okay to scope to one file, but still per-link confirmation.
- **"Just delete all the dead ones"** → still per-link confirmation. Users who say "just delete all of them" often change their mind when they see the list. This is a feature, not bureaucracy.

The only exception is when the user says "yes to everything below" *after seeing the list*. That's a specific, informed consent. Proceed in that case — but make it clear in the chat log exactly what you did.

---

## What janitor-claude does NOT audit

- **External URLs** (`http://`, `https://`, `mailto:`). Janitor is offline-only; checking HTTP status would require a network call, which is forbidden.
- **Image links** to local files that aren't `.md` (e.g. `![](images/foo.png)`). Out of scope for v0.1. A broken image in a markdown file is a smaller problem than a broken prose link.
- **Links inside code blocks** (```` ``` ````). These are almost always example code, not real links. Skip the audit inside fenced code blocks.
- **Anchor-only links** (`[text](#section)`). These resolve within the same file — only check that the anchor exists in the current file, don't treat them as file links.
