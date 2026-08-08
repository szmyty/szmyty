---
cssclasses:
  - moc
type: moc
tags:
  - moc
  - health
---

# 💚 Health

> Map of health, wellbeing, and lifestyle notes.

## 🌿 Overview

A living map for health tracking, habits, research, and reflections.

## 📋 Health Notes

```dataview
LIST
FROM "health"
WHERE file.name != "README"
SORT file.mtime DESC
```

## 🏋️ Fitness & Movement

- [[health/fitness|Fitness]]

## 🥗 Nutrition

- [[health/nutrition|Nutrition]]

## 😴 Sleep

- [[health/sleep|Sleep]]

## 🧘 Mental Health

- [[health/mental-health|Mental Health]]

## 📊 Health Journal

```dataview
LIST
FROM "journal/daily"
WHERE contains(tags, "health")
SORT file.name DESC
LIMIT 14
```

## 🔬 Health Research

```dataview
LIST
FROM "research"
WHERE contains(tags, "health")
SORT file.mtime DESC
```
