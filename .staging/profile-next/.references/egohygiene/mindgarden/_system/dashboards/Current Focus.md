---
cssclasses:
  - dashboard
tags:
  - dashboard
---

# 🎯 Current Focus

> Active projects, ongoing research, and current priorities.

## 🚀 Active Projects

```dataview
TABLE status, file.mtime as "Last Updated"
FROM "projects"
WHERE status = "active" AND file.name != "README"
SORT file.mtime DESC
```

## 🔄 In Progress

```dataview
TABLE status, file.mtime as "Last Updated"
FROM "projects"
WHERE status = "in-progress" AND file.name != "README"
SORT file.mtime DESC
```

## 📚 Active Research

```dataview
TABLE status, file.mtime as "Last Updated"
FROM "research"
WHERE status = "active" AND file.name != "README"
SORT file.mtime DESC
```

## ✅ Pending Tasks (All)

```dataviewjs
const tasks = dv.pages()
  .file.tasks
  .filter(t => !t.completed);

if (tasks.length === 0) {
  dv.paragraph("*No pending tasks. 🎉*");
} else {
  dv.taskList(tasks.sort(t => t.created, "desc").slice(0, 20), false);
}
```

## 📆 This Week's Journal

```dataview
LIST
FROM "journal/weekly"
SORT file.name DESC
LIMIT 1
```

## 📅 Recent Daily Notes

```dataview
LIST
FROM "journal/daily"
SORT file.name DESC
LIMIT 7
```

## 🧠 Recently Linked Concepts

```dataview
TABLE file.inlinks.length as "Inlinks", file.mtime as "Modified"
FROM "concepts"
WHERE file.name != "README"
SORT file.inlinks.length DESC
LIMIT 5
```
