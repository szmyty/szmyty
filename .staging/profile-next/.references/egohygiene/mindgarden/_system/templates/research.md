---
title: "<% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
status: active
type: research
tags:
  - research
---

# <% tp.file.title %>

## Research Question

> What am I trying to understand or answer?

## Hypothesis

## Background

## Methodology

## Findings

## Key Sources

```dataview
LIST
FROM "research/references"
WHERE contains(related, this.file.link)
```

## Synthesis

## Open Questions

- 
- 

## Next Steps

- [ ] 

## References

---

*Created: <% tp.date.now("YYYY-MM-DD") %>*
