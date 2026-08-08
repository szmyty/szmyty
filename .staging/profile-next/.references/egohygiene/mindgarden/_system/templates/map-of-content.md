---
title: "<% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: moc
tags:
  - moc
---

# <% tp.file.title %>

> A Map of Content for **<% tp.file.title %>** — a curated index linking related notes and ideas.

## 🗺 Overview

## 📌 Core Notes

- [[]]

## 🔗 Related Maps

- [[]]

## 📝 All Notes in This Domain

```dataview
LIST
FROM ""
WHERE contains(tags, "<% tp.file.title | lower %>")
SORT file.name ASC
```

---

*Created: <% tp.date.now("YYYY-MM-DD") %>*
