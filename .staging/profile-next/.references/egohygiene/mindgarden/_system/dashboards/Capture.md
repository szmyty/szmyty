---
cssclasses:
  - dashboard
tags:
  - dashboard
---

# 📥 Capture

> Quick capture for ideas, links, tasks, and fleeting notes.
> Process regularly — turn captures into permanent notes.

## ⚡ Quick Notes

New notes created in `notes/` folder, newest first.

```dataview
TABLE file.ctime as "Created", file.size as "Size"
FROM "notes"
WHERE file.name != "README"
SORT file.ctime DESC
LIMIT 15
```

## 🔖 Unprocessed Notes

Notes that have no `type` front-matter set yet (likely fleeting captures).

```dataview
LIST
FROM "" AND !"templates" AND !"assets" AND !".obsidian"
WHERE !type AND file.name != "README" AND !contains(file.folder, "dashboards")
SORT file.ctime ASC
LIMIT 20
```

## 📎 Notes Without Tags

```dataview
LIST
FROM "" AND !"templates" AND !"assets" AND !".obsidian"
WHERE !file.tags AND file.name != "README"
AND !contains(file.folder, "dashboards")
SORT file.ctime ASC
LIMIT 10
```

## 🔗 Orphaned Notes

Notes with no inbound or outbound links.

```dataview
LIST
FROM "" AND !"templates" AND !"assets" AND !".obsidian"
WHERE file.inlinks.length = 0 AND file.outlinks.length = 0
AND file.name != "README"
AND !contains(file.folder, "dashboards")
SORT file.ctime ASC
LIMIT 10
```

## 🗂 Process Checklist

- [ ] Review new notes in `notes/`
- [ ] Add type and tags to unprocessed notes
- [ ] Link orphaned notes to relevant MOCs
- [ ] Convert good ideas into permanent concept notes
