# Homelab Scripts

## sync-obsidian-roadmap.py

This script automatically syncs the roadmap from your Obsidian Publish page to the README.md file.

### How it works

1. **Fetches** the content from `https://publish.obsidian.md/gauranshmathur/Publish/Homelab`
2. **Parses** the HTML to extract roadmap items (To Do, In Progress, Done, etc.)
3. **Updates** the Roadmap section in README.md
4. **Preserves** all other content in the README

### Running manually

```bash
# From the project root
python scripts/sync-obsidian-roadmap.py
```

### GitHub Action

The script runs automatically every hour via GitHub Actions (`.github/workflows/sync-roadmap.yml`).

### Customization

If your Obsidian page structure changes, you may need to update the parsing logic in the `parse_roadmap_content()` function.

The script looks for:
- `- [ ]` pattern for unchecked items (To Do)
- `- [x]` pattern for checked items (Done)

### Troubleshooting

Check `.github/roadmap-sync-status.json` for the last sync status and any errors.