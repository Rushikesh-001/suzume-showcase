// ═══════════════════════════════════════════
// MARKDOWN PARSER — Pure Vanilla JS
// ═══════════════════════════════════════════

const mdRules = [
  // Headings
  { regex: /^###### (.+)$/gm, replace: '<h6>$1</h6>' },
  { regex: /^##### (.+)$/gm, replace: '<h5>$1</h5>' },
  { regex: /^#### (.+)$/gm, replace: '<h4>$1</h4>' },
  { regex: /^### (.+)$/gm, replace: '<h3>$1</h3>' },
  { regex: /^## (.+)$/gm, replace: '<h2>$1</h2>' },
  { regex: /^# (.+)$/gm, replace: '<h1>$1</h1>' },

  // Horizontal rules
  { regex: /^(---|\*\*\*|___)\s*$/gm, replace: '<hr>' },

  // Blockquotes
  { regex: /^> (.+)$/gm, replace: '<blockquote>$1</blockquote>' },

  // Images (must come before links)
  { regex: /!\[([^\]]*)\]\(([^)]+)\)/g, replace: '<img src="$2" alt="$1">' },

  // Links
  { regex: /\[([^\]]+)\]\(([^)]+)\)/g, replace: '<a href="$2" target="_blank" rel="noopener">$1</a>' },

  // Bold + Italic (order matters)
  { regex: /\*\*\*(.+?)\*\*\*/g, replace: '<strong><em>$1</em></strong>' },
  { regex: /___(.+?)___/g, replace: '<strong><em>$1</em></strong>' },

  // Bold
  { regex: /\*\*(.+?)\*\*/g, replace: '<strong>$1</strong>' },
  { regex: /__(.+?)__/g, replace: '<strong>$1</strong>' },

  // Italic
  { regex: /\*(.+?)\*/g, replace: '<em>$1</em>' },
  { regex: /_(.+?)_/g, replace: '<em>$1</em>' },

  // Inline code
  { regex: /`([^`]+)`/g, replace: '<code>$1</code>' },

  // Code blocks (fenced)
  { regex: /```(\w*)\n([\s\S]*?)```/g, replace: '<pre><code>$2</code></pre>' },
];

function parseMarkdown(text) {
  let html = text;

  // Apply all regex rules
  for (const rule of mdRules) {
    html = html.replace(rule.regex, rule.replace);
  }

  // Process lists
  html = processLists(html);

  // Process paragraphs (wrap non-block elements in <p>)
  html = processParagraphs(html);

  // Line breaks
  html = html.replace(/\n{2,}/g, '\n\n');

  return html;
}

function processLists(text) {
  const lines = text.split('\n');
  const result = [];
  let inUl = false;
  let inOl = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Unordered list
    const ulMatch = line.match(/^[\s]*[-*+]\s+(.+)$/);
    if (ulMatch) {
      if (inOl) { result.push('</ol>'); inOl = false; }
      if (!inUl) { result.push('<ul>'); inUl = true; }
      result.push(`<li>${ulMatch[1]}</li>`);
      continue;
    }

    // Ordered list
    const olMatch = line.match(/^[\s]*\d+\.\s+(.+)$/);
    if (olMatch) {
      if (inUl) { result.push('</ul>'); inUl = false; }
      if (!inOl) { result.push('<ol>'); inOl = true; }
      result.push(`<li>${olMatch[1]}</li>`);
      continue;
    }

    // Close lists
    if (inUl) { result.push('</ul>'); inUl = false; }
    if (inOl) { result.push('</ol>'); inOl = false; }
    result.push(line);
  }

  if (inUl) result.push('</ul>');
  if (inOl) result.push('</ol>');

  return result.join('\n');
}

function processParagraphs(text) {
  const lines = text.split('\n');
  const result = [];
  let inBlock = false;

  const blockTags = ['h1','h2','h3','h4','h5','h6','ul','ol','li','blockquote','pre','hr','<img'];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      if (!inBlock) result.push('');
      continue;
    }

    const startsWithBlock = blockTags.some(tag => trimmed.startsWith('<'+tag) || tag.startsWith('<'));
    const isBlock = startsWithBlock || trimmed.startsWith('<blockquote') ||
                    trimmed.startsWith('<pre') || trimmed.startsWith('<hr') ||
                    trimmed.startsWith('<ul') || trimmed.startsWith('<ol') ||
                    trimmed.startsWith('<h') || trimmed.startsWith('</ul') ||
                    trimmed.startsWith('</ol') || trimmed.startsWith('</blockquote') ||
                    trimmed.startsWith('</pre') || trimmed.startsWith('<img');

    if (isBlock) {
      if (!inBlock) { inBlock = true; }
      result.push(trimmed);
    } else {
      if (inBlock) { inBlock = false; }
      // Check if it's already wrapped in a block tag
      if (!trimmed.startsWith('<')) {
        result.push(`<p>${trimmed}</p>`);
      } else {
        result.push(trimmed);
      }
    }
  }

  return result.join('\n');
}

// ═══════════════════════════════════════════
// APP
// ═══════════════════════════════════════════

const editor = document.getElementById('editor');
const preview = document.getElementById('preview');
const wordCount = document.getElementById('wordCount');
const copyBtn = document.getElementById('copyBtn');

const defaultMarkdown = `# Welcome to Suzume's Markdown Editor

This is a **real-time markdown editor** built by Suzume, the Supreme AI Orchestrator.

## Why This Demo?

This demonstrates Suzume's ability to build **fully functional web applications**:

- **Custom markdown parser** — Written entirely in vanilla JavaScript (no libraries)
- **Real-time preview** — Updates as you type
- **Dark theme** — Premium UI with purple accents
- **Toolbar** — Quick-insert markdown syntax

### Try It Yourself

Type on the left, see the result on the right!

1. Write some **bold text** with \\*\\*asterisks\\*\\*
2. Add _italic text_ with \\_underscores\\_
3. Create [links](https://example.com)
4. Add \`inline code\` with backticks

> "The best way to predict the future is to invent it." — Alan Kay

\`\`\`
// Code blocks work too
function hello() {
  console.log("Hello, Suzume!");
}
\`\`\`

---

*Built with ❤️ by Suzume — July 2026*
`;

function update() {
  const text = editor.value;
  const html = parseMarkdown(text);
  preview.innerHTML = html;

  // Word count
  const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
  const chars = text.length;
  wordCount.textContent = `${words} words · ${chars} chars`;
}

// ─── Toolbar Actions ───
const syntaxMap = {
  bold: { before: '**', after: '**' },
  italic: { before: '*', after: '*' },
  heading: { before: '## ', after: '' },
  link: { before: '[', after: '](url)' },
  code: { before: '```\\n', after: '\\n```' },
  list: { before: '- ', after: '' },
  quote: { before: '> ', after: '' },
};

document.querySelectorAll('.tool-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const cmd = btn.dataset.cmd;
    const s = syntaxMap[cmd];
    if (!s) return;

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selected = editor.value.substring(start, end);
    const replacement = s.before + selected + s.after;

    editor.setRangeText(replacement, start, end, 'end');
    editor.focus();
    update();
  });
});

// ─── Copy HTML ───
copyBtn.addEventListener('click', () => {
  const html = preview.innerHTML;
  navigator.clipboard.writeText(html).then(() => {
    copyBtn.textContent = '✅ Copied!';
    setTimeout(() => { copyBtn.textContent = '📋 Copy HTML'; }, 2000);
  }).catch(() => {
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = html;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
    copyBtn.textContent = '✅ Copied!';
    setTimeout(() => { copyBtn.textContent = '📋 Copy HTML'; }, 2000);
  });
});

// ─── Init ───
editor.value = defaultMarkdown;
editor.addEventListener('input', update);
update();
