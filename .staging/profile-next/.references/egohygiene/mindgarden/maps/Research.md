---
cssclasses:
  - moc
type: moc
tags:
  - moc
  - research
---

# 🔬 Research

> Map of all research threads — active inquiries, completed studies, and references.

## 🔍 Active Inquiries

```dataview
TABLE status, file.mtime as "Updated"
FROM "research"
WHERE status = "active" AND file.name != "README"
SORT file.mtime DESC
```

## 📖 Reading List

```dataview
TABLE author, year, status
FROM ""
WHERE type = "book" AND (status = "reading" OR status = "to-read")
SORT status ASC, file.name ASC
```

## 📚 Completed Research

```dataview
TABLE status, file.mtime as "Updated"
FROM "research"
WHERE status = "completed" AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

## 🗂 Literature References

```dataview
TABLE authors, year
FROM "research/references"
WHERE file.name != "README"
SORT year DESC
LIMIT 20
```

## 💡 Concepts Explored

```dataview
TABLE file.inlinks.length as "Inlinks"
FROM "concepts"
WHERE file.name != "README"
SORT file.inlinks.length DESC
LIMIT 10
```

## 🧪 Experiments

```dataview
LIST
FROM "experiments"
WHERE file.name != "README"
SORT file.mtime DESC
```
