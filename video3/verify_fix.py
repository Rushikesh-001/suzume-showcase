"""Verify all home buttons are properly wrapped."""
import os
SHOWCASE = r'C:\Users\Rushikesh\suzume-showcase'
files = [
    'index.html','official/index.html','3d-demo/index.html',
    'demo-markdown/index.html','demo-canvas/index.html',
    'demo-game/index.html','saas-website/index.html','presentation/index.html'
]
all_ok = True
for f in files:
    path = os.path.join(SHOWCASE, f)
    with open(path, 'r', encoding='utf-8') as fp:
        c = fp.read()
    if '/* HOME BUTTON */' in c:
        idx = c.find('/* HOME BUTTON */')
        before = c[max(0,idx-20):idx]
        ok = '<style>' in before
        if not ok:
            print(f'FAIL: {f} - still bare CSS')
            all_ok = False
        else:
            print(f'OK: {f}')
if all_ok:
    print('\nAll 8 files properly fixed!')
