---
cssclasses:
  - moc
type: moc
tags:
  - moc
  - projects
---

# 🗂 Projects

> Map of all projects — active, in progress, and archived.
> Use this as your canonical project index.

## 🚀 Active

```dataview
TABLE status, file.mtime as "Updated"
FROM "projects"
WHERE status = "active" AND file.name != "README"
SORT file.mtime DESC
```

## 🔄 In Progress

```dataview
TABLE status, file.mtime as "Updated"
FROM "projects"
WHERE status = "in-progress" AND file.name != "README"
SORT file.mtime DESC
```

## ⏸ On Hold

```dataview
TABLE status, file.mtime as "Updated"
FROM "projects"
WHERE status = "on-hold" AND file.name != "README"
SORT file.mtime DESC
```

## ✅ Completed

```dataview
TABLE status, file.mtime as "Updated"
FROM "projects"
WHERE status = "completed" AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

## 🗄 Archived

```dataview
TABLE status, file.mtime as "Updated"
FROM "projects"
WHERE status = "archived" AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

## 📊 Project Stats

```dataviewjs
const projects = dv.pages('"projects"').filter(p => p.file.name !== "README");
const byStatus = {};
for (const p of projects) {
  const s = p.status ?? "unknown";
  byStatus[s] = (byStatus[s] ?? 0) + 1;
}
dv.table(
  ["Status", "Count"],
  Object.entries(byStatus).sort()
);
```
