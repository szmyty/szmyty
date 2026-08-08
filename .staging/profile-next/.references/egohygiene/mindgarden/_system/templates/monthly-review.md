---
date: <% tp.date.now("YYYY-MM-DD") %>
month: "<% tp.date.now("YYYY-MM") %>"
tags:
  - monthly-review
  - journal
---

# <% tp.date.now("MMMM YYYY") %> — Monthly Review

## 🎯 Monthly Theme

## 📊 By the Numbers

| Metric | Count |
| ------ | ----- |
| Notes Created | |
| Books Read | |
| Projects Completed | |
| Goals Met | |

## 🌟 Top Wins

1. 
2. 
3. 

## 🔄 Projects Review

```dataview
TABLE status, file.mtime as "Updated"
FROM "projects"
SORT status ASC, file.mtime DESC
```

## 📚 What I Learned

## 🚀 Next Month Goals

1. 
2. 
3. 

## 💬 Overall Reflection

---

← [[<% tp.date.now("YYYY-MM", -31) %>]] | [[<% tp.date.now("YYYY-MM", 31) %>]] →
