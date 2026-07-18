"""Fix home button CSS injection bug - wrap in <style> tags properly."""
import os, re

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

for fname in files:
    path = os.path.join(SHOWCASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if there's bare CSS (home-btn rules not wrapped in <style>)
    # Pattern: the CSS starts right after <link> or </head> opening
    if '/* HOME BUTTON */' in content:
        # Check if it's inside <style> tags already
        if '<style>\n\n/* HOME BUTTON */' in content or '<style>\n/* HOME BUTTON */' in content:
            print(f'OK (already styled): {fname}')
            continue
        
        # Find the HOME BUTTON block
        start = content.find('/* HOME BUTTON */')
        # Find the end: look for </head> after start, then go back to find CSS end
        end_head = content.find('</head>', start)
        
        if end_head > start:
            # The CSS is between start and end_head
            css_block = content[start:end_head].rstrip()
            
            # Replace bare CSS with <style> wrapped version
            old = css_block
            new = f'<style>\n{css_block}\n</style>\n'
            
            content = content[:start] + new + content[end_head:]
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'FIXED: {fname}')
        else:
            print(f'SKIP (unexpected structure): {fname}')
    else:
        print(f'SKIP (no home button): {fname}')

print('\n=== Verifying ===')
for fname in files:
    path = os.path.join(SHOWCASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    if '/* HOME BUTTON */' in c:
        # Check it's wrapped
        idx = c.find('/* HOME BUTTON */')
        before = c[max(0,idx-20):idx]
        if '<style>' in before:
            print(f'  ✓ {fname} - properly styled')
        else:
            print(f'  ✗ {fname} - still bare CSS!')
