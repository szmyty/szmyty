name: 🔁 CI/CD Improvements
description: Suggest improvements to automation, testing, builds, or deployments.
title: "[CI/CD] "
labels: ["ci-cd", "devops"]
assignees: []

body:

- type: textarea
  id: pipeline
  attributes:
  label: Pipeline or Automation to Improve
  description: Which job or process needs attention?
- type: textarea
  id: bottleneck
  attributes:
  label: Current Issue or Limitation
  description: What's slow, flaky, or hard to manage?
- type: textarea
  id: recommendation
  attributes:
  label: Suggested Change
  description: How might this be improved? Feel free to include workflows or tools.
- type: textarea
  id: confidence
  attributes:
  label: Level of Confidence
  description: How confident are you that this will help? (1-5 or qualitative)
