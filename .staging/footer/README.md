# Footer Components

This directory contains the enhanced footer content for the README.md profile page.

## Files

- **`footer.html`** - Enhanced footer with open-source community badges and contact information

## Features

The enhanced footer includes:

### 🤝 Open Source Community Badges
- Open Collective
- Linux Foundation
- CNCF (Cloud Native Computing Foundation)
- Mozilla
- FSF (Free Software Foundation)
- Creative Commons
- EFF (Electronic Frontier Foundation)
- Apache Foundation
- Open Source Initiative (OSI)

### 📬 Contact Information
- GitHub profile link
- Email contact
- LinkedIn profile

### 🛠️ Built With
- GitHub Actions badge
- Python badge
- Poetry badge

## Usage

The footer content is currently embedded directly in `README.md`. To update the footer:

1. Edit `footer/footer.html` with your changes
2. Manually sync the changes to the footer section in `README.md`

### Future Enhancement

To enable automated footer injection via GitHub Actions:

1. Add footer markers to README.md:
   ```html
   <!-- FOOTER:START -->
   [footer content here]
   <!-- FOOTER:END -->
   ```

2. Update the `parallel-fetch.yml` workflow to run:
   ```bash
   python scripts/update-readme.py --marker FOOTER --content-file footer/footer.html
   ```

## Customization

### Adding More Badges

To add additional community or project badges, use the shields.io format:

```markdown
[![Badge Name](https://img.shields.io/badge/Badge-Name-COLOR?style=for-the-badge&logo=LOGO)](URL)
```

**Badge Colors** (from the theme):
- Primary: `4a4e69`
- Accent: `436fb5`
- Success: `3da639`
- Warning: `ef9421`
- Error: `d32027`

### GitHub-Safe HTML

The footer uses only GitHub-supported HTML elements:
- `<div align="center">` - for centering content
- `<img>` - for the footer SVG banner
- `<br/>` - for spacing
- `<h2>`, `<h3>` - for section headings
- Standard Markdown badges

All HTML is fully compliant with GitHub-flavored Markdown specifications.

## Design Philosophy

The footer is designed to:
1. **Showcase community involvement** - Display support for open-source initiatives
2. **Provide clear contact methods** - Make it easy to connect
3. **Maintain visual consistency** - Match the profile's color scheme and style
4. **Respect GitHub constraints** - Use only supported HTML/Markdown features
5. **Work across devices** - Responsive on desktop and mobile
6. **Support light/dark modes** - Badges adapt to GitHub's theme

---

*For the main README style guide, see [docs/markdown_valid_elements.md](../docs/markdown_valid_elements.md)*
