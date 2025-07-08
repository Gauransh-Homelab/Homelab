#!/usr/bin/env python3
"""
Sync Obsidian roadmap to README.md
This script fetches content from Obsidian Publish and updates the roadmap section in README.
"""

import requests
import re
import os
import sys
from datetime import datetime
import json

OBSIDIAN_URL = "https://publish.obsidian.md/gauranshmathur/Publish/Homelab"
README_PATH = "README.md"

def fetch_obsidian_content():
    """Fetch content from Obsidian Publish"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Homelab Roadmap Sync)'
    }
    
    try:
        response = requests.get(OBSIDIAN_URL, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching Obsidian content: {e}")
        return None

def parse_roadmap_content(html_content):
    """
    Parse the roadmap content from HTML
    This is a simplified parser - adjust based on actual HTML structure
    """
    sections = {
        "to_do": [],
        "in_progress": [],
        "done": [],
        "future_projects": [],
        "archive": []
    }
    
    # This parsing logic will need to be adjusted based on the actual HTML structure
    # For now, we'll use regex patterns to find common patterns
    
    # Try to find checkbox lists (common in Obsidian)
    todo_pattern = r'- \[ \] (.+?)(?=\n|$)'
    done_pattern = r'- \[x\] (.+?)(?=\n|$)'
    
    # Find all unchecked items (To Do)
    for match in re.finditer(todo_pattern, html_content):
        item = match.group(1).strip()
        sections["to_do"].append(item)
    
    # Find all checked items (Done)
    for match in re.finditer(done_pattern, html_content):
        item = match.group(1).strip()
        sections["done"].append(item)
    
    return sections

def generate_roadmap_section(sections=None):
    """Generate the roadmap section for README"""
    
    roadmap = """## 📋 Roadmap

<div align="center">

[![Live Roadmap](https://img.shields.io/badge/Live%20Roadmap-View%20on%20Obsidian-7c3aed?style=for-the-badge&logo=obsidian&logoColor=white)](https://publish.obsidian.md/gauranshmathur/Publish/Homelab)

*The roadmap is actively maintained in Obsidian for real-time updates*

</div>

### 🔗 Quick Links

- 📊 **[Current Progress](https://publish.obsidian.md/gauranshmathur/Publish/Homelab)** - Live Kanban board
- ✅ **[Completed Items](https://publish.obsidian.md/gauranshmathur/Publish/Homelab#archive)** - Archive of finished tasks
- 🚀 **[Future Projects](https://publish.obsidian.md/gauranshmathur/Publish/Homelab#future-projects)** - Long-term plans
"""

    if sections and any(sections.values()):
        roadmap += "\n### 📌 Current Status (Auto-synced)\n\n"
        
        if sections.get('in_progress'):
            roadmap += "#### 🚧 In Progress\n"
            for item in sections['in_progress']:
                roadmap += f"- {item}\n"
            roadmap += "\n"
        
        if sections.get('to_do'):
            roadmap += "#### 📋 To Do (Top Items)\n"
            for item in sections['to_do'][:10]:
                roadmap += f"- {item}\n"
            if len(sections['to_do']) > 10:
                roadmap += f"- *...and {len(sections['to_do']) - 10} more items*\n"
            roadmap += "\n"
        
        roadmap += f"> 🔄 **Last synced**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
    else:
        # Fallback content when parsing fails
        roadmap += """
### 📌 Current Focus Areas

Based on the live roadmap, the main priorities are:

1. **Infrastructure**: ArgoCD for GitOps, LGTM monitoring stack
2. **Security**: Authentik SSO, Cloudflare IP whitelisting
3. **Performance**: PostgreSQL HA, *arr stack database migration
4. **User Experience**: Homarr dashboard, automation with n8n

> 💡 **Note**: Check the [live roadmap](https://publish.obsidian.md/gauranshmathur/Publish/Homelab) for the most up-to-date task list and progress.
"""
    
    return roadmap

def update_readme(new_roadmap_content):
    """Update the README file with new roadmap content"""
    
    if not os.path.exists(README_PATH):
        print(f"README.md not found at {README_PATH}")
        return False
    
    with open(README_PATH, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Find roadmap section
    roadmap_start = readme_content.find('## 📋 Roadmap')
    if roadmap_start == -1:
        print("Roadmap section not found in README")
        return False
    
    # Find the end of roadmap section (next section or end of file)
    roadmap_end = readme_content.find('\n---\n', roadmap_start)
    if roadmap_end == -1:
        roadmap_end = readme_content.find('\n## ', roadmap_start + 1)
    if roadmap_end == -1:
        roadmap_end = len(readme_content)
    
    # Replace roadmap section
    new_readme = (
        readme_content[:roadmap_start] + 
        new_roadmap_content + 
        readme_content[roadmap_end:]
    )
    
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_readme)
    
    return True

def main():
    """Main sync function"""
    print("🔄 Syncing roadmap from Obsidian...")
    
    # Fetch content
    html_content = fetch_obsidian_content()
    if not html_content:
        print("❌ Failed to fetch Obsidian content")
        sys.exit(1)
    
    # Parse content
    sections = parse_roadmap_content(html_content)
    
    # Generate new roadmap section
    new_roadmap = generate_roadmap_section(sections)
    
    # Update README
    if update_readme(new_roadmap):
        print("✅ README updated successfully!")
        
        # Save sync status
        status = {
            'last_sync': datetime.utcnow().isoformat(),
            'sections_found': {k: len(v) for k, v in sections.items()},
            'success': True
        }
        
        os.makedirs('.github', exist_ok=True)
        with open('.github/roadmap-sync-status.json', 'w') as f:
            json.dump(status, f, indent=2)
    else:
        print("❌ Failed to update README")
        sys.exit(1)

if __name__ == "__main__":
    main()