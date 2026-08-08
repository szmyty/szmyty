---
date: <% tp.date.now("YYYY-MM-DD") %>
week: "<% tp.date.now("YYYY-[W]WW") %>"
tags:
  - weekly-review
  - journal
---

# Week <% tp.date.now("WW") %> — <% tp.date.now("YYYY") %>

> **Period:** <% tp.date.now("MMMM D", 0, "YYYY-[W]WW", 1) %> – <% tp.date.now("MMMM D", 0, "YYYY-[W]WW", 7) %>

## 🎯 Theme of the Week

## 🌟 Highlights

- 
- 
- 

## ✅ Wins

What went particularly well this week?

## 🚧 Challenges

What didn't go as planned?

## 📚 Key Learnings

What did I learn or discover?

1. 
2. 
3. 

## 🔄 Projects Update

```dataview
TABLE status, file.mtime as "Updated"
FROM "projects"
WHERE status = "active"
SORT file.mtime DESC
```

## 📅 Next Week's Priorities

1. 
2. 
3. 

## 🔗 Notes Created This Week

```dataview
LIST
FROM ""
WHERE file.ctime >= date("<% tp.date.now("YYYY-MM-DD", -6) %>")
AND !contains(file.folder, "templates")
AND !contains(file.folder, "journal")
SORT file.ctime ASC
```

## 💬 Reflections

---

← [[<% tp.date.now("YYYY-[W]WW", -7) %>]] | [[<% tp.date.now("YYYY-[W]WW", 7) %>]] →
