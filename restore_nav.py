import os
import re

def add_nav_icons(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if icons are already present
    if '<div class="nav-icons">' in content and 'account_circle' in content:
        print(f"Icons already present in: {file_path}")
        return
    
    # Pattern to match the removed navigation icons comment or empty header
    pattern = r'(<div class="logo">.*?<h1>Consultigo</h1>\s*</div>)\s*(<!-- Navigation icons removed -->|\s*)(</header>)'
    
    # The navigation icons HTML to add
    replacement = r'\1\n            <div class="nav-icons">\n                <span class="material-icons" title="Profile">account_circle</span>\n                <span class="material-icons" title="Logout">logout</span>\n            </div>\n        \3'
    
    # Replace the comment with the new HTML
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print(f"Added nav icons to: {file_path}")

def main():
    # Directory containing the HTML files
    frontend_dir = 'frontend'
    
    # List of HTML files to update (all except index.html)
    html_files = [
        os.path.join(frontend_dir, 'examples.html'),
        os.path.join(frontend_dir, 'frameworks.html'),
        os.path.join(frontend_dir, 'case-detail.html'),
        os.path.join(frontend_dir, 'guesstimates.html'),
        os.path.join(frontend_dir, 'guesstimate-detail.html')
    ]
    
    # Update each file
    for file_path in html_files:
        if os.path.exists(file_path):
            add_nav_icons(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
    print("Navigation icons added to content pages") 