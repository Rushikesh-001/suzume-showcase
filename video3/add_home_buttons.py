"""Add Home buttons to all HTML pages in suzume-showcase."""
import os

SHOWCASE = r'C:\Users\Rushikesh\suzume-showcase'

files = [
    'index.html',
    'official/index.html',
    '3d-demo/index.html',
    'demo-markdown/index.html',
    'demo-canvas/index.html',
    'demo-game/index.html',
    'saas-website/index.html',
    'presentation/index.html',
]

home_html_template = '''<!-- HOME BUTTON -->
<a href="%s" class="home-btn" title="Back to Suzume Showcase">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>
  <span>Home</span>
</a>
'''

home_css = '''

/* HOME BUTTON */
.home-btn {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 99999;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: rgba(10,10,30,0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,195,80,0.3);
    border-radius: 25px;
    color: #ffc350;
    text-decoration: none;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.home-btn:hover {
    background: rgba(255,195,80,0.15);
    border-color: #ffc350;
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(255,195,80,0.2);
}
.home-btn svg {
    width: 18px;
    height: 18px;
}
@media (max-width: 768px) {
    .home-btn {
        top: 10px;
        left: 10px;
        padding: 6px 12px;
        font-size: 12px;
    }
    .home-btn span {
        display: none;
    }
}

'''

for fname in files:
    path = os.path.join(SHOWCASE, fname)
    if not os.path.exists(path):
        print(f'MISSING: {fname}')
        continue
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if home button already exists
    if 'home-btn' in content:
        print(f'ALREADY HAS: {fname}')
        continue
    
    # Determine href based on depth
    depth = fname.count('/')
    if depth == 0:
        href = '.'
    else:
        href = '../' * depth
    
    # Add CSS before </head>
    if '</head>' in content:
        # Inject before </head>
        insert_pos = content.find('</head>')
        content = content[:insert_pos] + home_css + content[insert_pos:]
    
    # Add HTML before </body>
    if '</body>' in content:
        html_block = home_html_template % href
        insert_pos = content.rfind('</body>')
        content = content[:insert_pos] + html_block + content[insert_pos:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'ADDED HOME BUTTON: {fname} (link="{href}")')

print('\nDone!')
