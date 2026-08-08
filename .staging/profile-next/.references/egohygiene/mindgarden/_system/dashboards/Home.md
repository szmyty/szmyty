---
cssclasses:
  - dashboard
  - home
tags:
  - dashboard
---

# 🏡 Garden

> Your personal knowledge foundation — a living second brain.

## 📌 Navigation

| Area | Link | Purpose |
| ---- | ---- | ------- |
| 🎯 Focus | [[dashboards/Current Focus\|Current Focus]] | Active projects and priorities |
| 📥 Capture | [[dashboards/Capture\|Capture]] | Quick capture and inbox |
| 🗂 Projects | [[maps/Projects\|Projects MOC]] | All projects overview |
| 🔬 Research | [[maps/Research\|Research MOC]] | Active research threads |
| 💚 Health | [[maps/Health\|Health MOC]] | Health and wellbeing |

## 📅 Today

```dataview
LIST
FROM "journal/daily"
WHERE file.name = dateformat(date(today), "yyyy-MM-dd")
LIMIT 1
```

## ✅ Active Tasks

```dataviewjs
const tasks = dv.pages()
  .file.tasks
  .filter(t => !t.completed && !t.text.includes("#someday"));

if (tasks.length === 0) {
  dv.paragraph("*No active tasks. Well done! 🎉*");
} else {
  dv.taskList(tasks.sort(t => t.created, "desc").slice(0, 10), false);
}
```

## 📝 Recently Modified

```dataview
TABLE file.mtime as "Modified", file.folder as "Folder"
FROM "" AND !"dashboards" AND !"templates" AND !".obsidian"
WHERE file.name != "README"
SORT file.mtime DESC
LIMIT 8
```

## 🗺 Maps of Content

```dataview
LIST
FROM "maps"
WHERE file.name != "README"
SORT file.name ASC
```

## 📊 Vault Stats

```dataviewjs
const pages = dv.pages('!"templates" and !"assets" and !".obsidian"');
const notes = pages.filter(p => !p.file.name.includes("README")).length;
const tasks = pages.file.tasks;
const completed = tasks.filter(t => t.completed).length;
const pending = tasks.filter(t => !t.completed).length;

dv.table(
  ["Metric", "Count"],
  [
    ["📄 Total Notes", notes],
    ["✅ Completed Tasks", completed],
    ["⏳ Pending Tasks", pending],
  ]
);
```
