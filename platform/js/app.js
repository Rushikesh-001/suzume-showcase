/**
 * SUZUME MAIN APPLICATION
 * Orchestrates all modules — navigation, rendering, events
 * The heart of the Suzume Platform
 */

(async function() {
  'use strict';

  // ===== APP STATE =====
  const App = {
    currentView: 'home',
    theme: 'dark',
    userName: 'Rushikesh'
  };

  // ===== DOM REFS =====
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ===== INITIALIZATION =====
  async function init() {
    try {
      // Open database
      await SuzumeDB.open();

      // Load stored data
      await Promise.all([
        SuzumeMemory.load(),
        SuzumeFiles.load()
      ]);

      // Load settings
      await loadSettings();

      // Setup all systems
      setupSplash();
      setupNavigation();
      setupTheme();
      setupChat();
      setupMemory();
      setupFiles();
      setupSettings();
      setupModals();
      setupSakuraCanvas();

      // Render initial data
      await refreshDashboard();
      await refreshChatHistory();

      // Close splash after everything is ready
      closeSplash();

      console.log('✨ Suzume Platform initialized successfully');
    } catch (e) {
      console.error('Init error:', e);
      document.getElementById('splash').classList.add('hidden');
    }
  }

  // ===== SPLASH SCREEN =====
  function setupSplash() {
    const statusEl = document.querySelector('.splash-status');
    const messages = [
      'Initializing neural network',
      'Loading memory banks',
      'Calibrating agent team',
      'Warming up sakura engine',
      'Almost ready...'
    ];
    let i = 0;
    const interval = setInterval(() => {
      i++;
      if (i < messages.length && statusEl) {
        statusEl.textContent = messages[i];
      }
    }, 500);
    
    // Store for cleanup
    window._splashInterval = interval;
  }

  function closeSplash() {
    setTimeout(() => {
      const splash = document.getElementById('splash');
      if (splash) {
        splash.classList.add('hidden');
      }
      if (window._splashInterval) {
        clearInterval(window._splashInterval);
      }
    }, 2200);
  }

  // ===== NAVIGATION =====
  function setupNavigation() {
    // Nav link clicks
    document.querySelectorAll('[data-nav]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const viewName = link.dataset.nav;
        navigateTo(viewName);
      });
    });

    // Hamburger menu
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    if (hamburger && navLinks) {
      hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('open');
      });

      // Close menu on link click
      navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
          hamburger.classList.remove('active');
          navLinks.classList.remove('open');
        });
      });
    }

    // Handle back/forward browser buttons
    window.addEventListener('popstate', (e) => {
      if (e.state && e.state.view) {
        switchView(e.state.view);
      }
    });
  }

  function navigateTo(viewName) {
    // Update URL
    const url = new URL(window.location);
    url.hash = viewName;
    window.history.pushState({ view: viewName }, '', url);
    switchView(viewName);
  }

  function switchView(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    
    // Remove active from nav links
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    // Show target view
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
      targetView.classList.add('active');
    }

    // Activate nav link
    const navLink = document.querySelector(`[data-nav="${viewName}"]`);
    if (navLink) {
      navLink.classList.add('active');
    }

    App.currentView = viewName;

    // Refresh view-specific data
    if (viewName === 'home') refreshDashboard();
    if (viewName === 'chat') scrollChatToBottom();
    if (viewName === 'memory') renderMemory();
    if (viewName === 'files') renderFiles();
  }

  // ===== THEME =====
  function setupTheme() {
    // Apply saved theme
    document.documentElement.setAttribute('data-theme', App.theme);

    // Theme toggle button in nav
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', toggleTheme);
    }

    // Theme toggle in settings
    const settingsToggle = document.getElementById('settingsThemeToggle');
    if (settingsToggle) {
      settingsToggle.checked = App.theme === 'light';
      settingsToggle.addEventListener('change', () => {
        toggleTheme();
      });
    }
  }

  function toggleTheme() {
    App.theme = App.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', App.theme);
    SuzumeDB.setSetting('theme', App.theme);

    // Sync settings toggle
    const settingsToggle = document.getElementById('settingsThemeToggle');
    if (settingsToggle) {
      settingsToggle.checked = App.theme === 'light';
    }
  }

  // ===== SETTINGS LOADING =====
  async function loadSettings() {
    try {
      const savedTheme = await SuzumeDB.getSetting('theme');
      if (savedTheme) App.theme = savedTheme;

      const savedName = await SuzumeDB.getSetting('userName');
      if (savedName) App.userName = savedName;
    } catch (e) {
      console.warn('Could not load settings:', e.message);
    }
  }

  // ===== DASHBOARD =====
  async function refreshDashboard() {
    try {
      // Update welcome name
      const userNameEl = document.getElementById('userName');
      if (userNameEl) userNameEl.textContent = App.userName;

      // Stats
      const chatCount = await SuzumeChat.getMessageCount();
      const memories = SuzumeMemory.getAll().length;
      const files = SuzumeFiles.getAll().length;
      const links = SuzumeMemory.getAll().filter(m => m.type === 'link').length;

      animateNumber('statChats', chatCount);
      animateNumber('statMemories', memories);
      animateNumber('statFiles', files);
      animateNumber('statLinks', links);

      // Activity feed
      await renderActivity();
    } catch (e) {
      console.warn('Dashboard refresh error:', e);
    }
  }

  function animateNumber(elId, target) {
    const el = document.getElementById(elId);
    if (!el) return;
    
    // For large numbers, just show immediately
    if (target > 100) {
      el.textContent = target.toLocaleString();
      return;
    }

    // Animate for small numbers
    let current = 0;
    const step = Math.max(1, Math.ceil(target / 20));
    const interval = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(interval);
      }
      el.textContent = current;
    }, 40);
  }

  async function renderActivity() {
    const feed = document.getElementById('activityFeed');
    if (!feed) return;

    try {
      const activities = await SuzumeDB.getActivity();
      
      if (!activities || activities.length === 0) {
        feed.innerHTML = `
          <div class="activity-empty">
            <div class="empty-icon">✨</div>
            <p>Your activity will appear here</p>
            <p class="empty-sub">Start chatting or upload files to see your history</p>
          </div>
        `;
        return;
      }

      const recent = activities.slice(0, 10);
      feed.innerHTML = recent.map(a => {
        const time = formatTime(a.timestamp);
        const colors = ['#FF6B9D', '#7C4DFF', '#00E5FF', '#FFD700', '#10B981', '#F59E0B'];
        const color = colors[a.id % colors.length];
        return `
          <div class="activity-item">
            <div class="activity-dot" style="background:${color}"></div>
            <div class="activity-content">
              <div class="activity-text">${a.icon} ${a.text}</div>
              <div class="activity-time">${time}</div>
            </div>
          </div>
        `;
      }).join('');
    } catch (e) {
      feed.innerHTML = `<div class="activity-empty"><p>Unable to load activity</p></div>`;
    }
  }

  // ===== CHAT =====
  function setupChat() {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSend');
    const attachBtn = document.getElementById('chatAttach');
    const fileInput = document.getElementById('chatFileInput');
    const clearBtn = document.getElementById('chatClear');

    // Send on button click
    if (sendBtn) {
      sendBtn.addEventListener('click', () => sendMessage());
    }

    // Send on Enter (Shift+Enter for newline)
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
    }

    // Attach file
    if (attachBtn && fileInput) {
      attachBtn.addEventListener('click', () => fileInput.click());
      fileInput.addEventListener('change', async (e) => {
        const files = e.target.files;
        if (files && files.length > 0) {
          // Show the files in chat
          const fileList = Array.from(files);
          const fileNames = fileList.map(f => `📎 ${f.name}`).join('\n');
          appendMessage('user', `Uploading ${fileList.length} file(s):\n${fileNames}`);
          
          // Actually upload
          const results = await SuzumeFiles.uploadMultiple(fileList);
          const successCount = results.length;
          
          setTimeout(async () => {
            const botMsg = `I've processed **${successCount}** file(s) successfully! They're now stored in my memory.\n\nYou can view them in the **Files** section, or ask me questions about them.`;
            const result = await SuzumeChat.send(botMsg);
            if (result) appendMessage('assistant', result.bot.content);
          }, 500);
        }
        fileInput.value = '';
      });
    }

    // Clear chat
    if (clearBtn) {
      clearBtn.addEventListener('click', async () => {
        if (confirm('Clear all chat messages?')) {
          await SuzumeChat.clear();
          document.getElementById('chatMessages').innerHTML = '';
          addWelcomeMessage();
        }
      });
    }
  }

  async function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    input.style.height = 'auto';

    // Show user message
    appendMessage('user', text);

    // Show typing indicator
    showTypingIndicator();

    // Get response
    const result = await SuzumeChat.send(text);

    // Remove typing indicator
    hideTypingIndicator();

    if (result && result.bot) {
      appendMessage('assistant', result.bot.content);
    }

    scrollChatToBottom();
  }

  function appendMessage(role, content) {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    // Remove empty state if present
    const empty = container.querySelector('.activity-empty');
    if (empty) empty.remove();

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role === 'user' ? 'user-msg' : 'suzume-msg'}`;

    const isUser = role === 'user';
    const time = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

    msgDiv.innerHTML = `
      ${!isUser ? `<div class="msg-avatar">
        <svg width="28" height="28" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="32" r="28" stroke="#FF6B9D" stroke-width="1" fill="rgba(255,107,157,0.1)"/>
          <path d="M32 14 C32 14 22 24 22 33 C22 38.5 26.5 43 32 43 C37.5 43 42 38.5 42 33 C42 24 32 14 32 14Z" fill="url(#chat-grad)" opacity="0.6"/>
        </svg>
      </div>` : ''}
      <div class="msg-content">
        <div class="msg-bubble">${formatMessage(content)}</div>
        <span class="msg-time">${time}</span>
      </div>
    `;

    container.appendChild(msgDiv);
    scrollChatToBottom();
  }

  function formatMessage(text) {
    if (!text) return '';
    // Convert markdown-like formatting
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Inline code
      .replace(/`(.*?)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 6px;border-radius:4px;font-size:0.85em">$1</code>')
      // Code block
      .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre style="background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;overflow-x:auto;font-size:0.85rem;line-height:1.4;margin:8px 0"><code>$2</code></pre>')
      // Unordered list
      .replace(/^- (.*?)(?:\n|$)/gm, '<li style="margin-bottom:2px">$1</li>')
      // Newlines
      .replace(/\n/g, '<br>');

    // Wrap consecutive <li> in <ul>
    html = html.replace(/((?:<li[^>]*>.*?<\/li>)+)/g, '<ul style="margin:6px 0;padding-left:20px">$1</ul>');

    return html;
  }

  function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    // Remove existing indicator
    hideTypingIndicator();

    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.id = 'typingIndicator';
    div.innerHTML = `
      <div class="msg-avatar">
        <svg width="28" height="28" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="32" r="28" stroke="#FF6B9D" stroke-width="1" fill="rgba(255,107,157,0.1)"/>
          <path d="M32 14 C32 14 22 24 22 33 C22 38.5 26.5 43 32 43 C37.5 43 42 38.5 42 33 C42 24 32 14 32 14Z" fill="url(#chat-grad)" opacity="0.6"/>
        </svg>
      </div>
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    `;
    container.appendChild(div);
    scrollChatToBottom();
  }

  function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
  }

  async function refreshChatHistory() {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    const messages = await SuzumeChat.loadHistory();
    
    // Clear and re-render
    container.innerHTML = '';

    if (messages.length === 0) {
      addWelcomeMessage();
      return;
    }

    // Show last 50 messages
    const recent = messages.slice(-50);
    recent.forEach(msg => {
      appendMessage(msg.role, msg.content);
    });

    scrollChatToBottom();
  }

  function addWelcomeMessage() {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    container.innerHTML = '';

    appendMessage('assistant', `Hello ${App.userName}! I'm Suzume, your Supreme AI Companion. 💜\n\nI can help you with:\n- 💬 Chatting about anything\n- 📁 Processing your files, images, documents\n- 🧠 Remembering everything you teach me\n- 🔗 Saving links, notes, and ideas\n- 🎨 Building websites, games, and applications\n\n*What would you like to do today?*`);
  }

  function scrollChatToBottom() {
    const container = document.getElementById('chatMessages');
    if (container) {
      setTimeout(() => {
        container.scrollTop = container.scrollHeight;
      }, 50);
    }
  }

  // ===== MEMORY VIEW =====
  function setupMemory() {
    // Search
    const searchInput = document.getElementById('memorySearch');
    if (searchInput) {
      searchInput.addEventListener('input', () => renderMemory());
    }

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderMemory();
      });
    });

    // Add memory button
    const addBtn = document.getElementById('addMemoryBtn');
    if (addBtn) {
      addBtn.addEventListener('click', () => {
        document.getElementById('addMemoryModal').classList.add('active');
      });
    }

    // Memory type selector in modal
    document.querySelectorAll('.mem-type-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.mem-type-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const type = btn.dataset.type;
        document.getElementById('memContentGroup').style.display = type === 'note' ? 'block' : 'none';
        document.getElementById('memUrlGroup').style.display = type === 'link' ? 'block' : 'none';
      });
    });

    // Save memory
    const saveBtn = document.getElementById('saveMemoryBtn');
    if (saveBtn) {
      saveBtn.addEventListener('click', async () => {
        const type = document.querySelector('.mem-type-btn.active')?.dataset.type || 'note';
        const title = document.getElementById('memTitle').value.trim();
        const content = document.getElementById('memContent').value.trim();
        const url = document.getElementById('memUrl').value.trim();
        const tagsStr = document.getElementById('memTags').value.trim();
        const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(Boolean) : [];

        if (!title) {
          showToast('Please enter a title', 'error');
          return;
        }

        try {
          if (type === 'note') {
            await SuzumeMemory.addNote(title, content, tags);
          } else {
            if (!url) {
              showToast('Please enter a URL', 'error');
              return;
            }
            await SuzumeMemory.addLink(title, url, tags);
          }

          showToast('Saved to memory! 🧠');
          closeModal('addMemoryModal');
          renderMemory();

          // Reset form
          document.getElementById('memTitle').value = '';
          document.getElementById('memContent').value = '';
          document.getElementById('memUrl').value = '';
          document.getElementById('memTags').value = '';
        } catch (e) {
          showToast('Error saving memory', 'error');
        }
      });
    }
  }

  function renderMemory() {
    const grid = document.getElementById('memoryGrid');
    if (!grid) return;

    const searchQuery = document.getElementById('memorySearch')?.value || '';
    const activeFilter = document.querySelector('.filter-btn.active')?.dataset?.filter || 'all';

    let items = SuzumeMemory.getAll();

    // Filter by type
    if (activeFilter !== 'all') {
      items = items.filter(m => m.type === activeFilter);
    }

    // Search
    if (searchQuery) {
      items = SuzumeMemory.search(searchQuery);
    }

    if (items.length === 0) {
      grid.innerHTML = `
        <div class="memory-empty" style="grid-column:1/-1">
          <div class="empty-icon">🧠</div>
          <p>${searchQuery ? 'No matching memories found' : 'Your memory is empty'}</p>
          <p class="empty-sub">${searchQuery ? 'Try a different search term' : 'Save notes, links, and files to build Suzume\'s knowledge'}</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = items.map(m => {
      const icon = m.type === 'note' ? '📝' : m.type === 'link' ? '🔗' : '📁';
      const time = SuzumeFiles.formatDate(m.timestamp);
      const tags = m.tags || [];

      // Truncate content
      const preview = m.content ? m.content.substring(0, 200) : '';

      return `
        <div class="memory-card glass" data-id="${m.id}">
          <div class="card-type">${icon} ${m.type}</div>
          <div class="card-title">${escapeHtml(m.title || 'Untitled')}</div>
          ${preview ? `<div class="card-preview">${escapeHtml(preview)}${m.content.length > 200 ? '...' : ''}</div>` : ''}
          ${m.url ? `<div class="card-link">🔗 ${escapeHtml(m.url)}</div>` : ''}
          ${tags.length ? `<div class="card-tags">${tags.map(t => `<span class="card-tag">${escapeHtml(t)}</span>`).join('')}</div>` : ''}
          <div class="card-date">${time}</div>
        </div>
      `;
    }).join('');

    // Click to view/delete
    grid.querySelectorAll('.memory-card').forEach(card => {
      card.addEventListener('click', async () => {
        const id = parseInt(card.dataset.id);
        if (confirm('Delete this memory?')) {
          await SuzumeMemory.remove(id);
          renderMemory();
          showToast('Memory deleted');
        }
      });
    });
  }

  // ===== FILES VIEW =====
  function setupFiles() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');

    if (uploadArea && fileInput) {
      // Click to upload
      if (uploadBtn) {
        uploadBtn.addEventListener('click', () => fileInput.click());
      }
      uploadArea.addEventListener('click', (e) => {
        if (e.target !== uploadBtn) fileInput.click();
      });

      // Drag and drop
      uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
      });
      uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
      });
      uploadArea.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
          await handleFiles(files);
        }
      });

      // File input change
      fileInput.addEventListener('change', async (e) => {
        const files = e.target.files;
        if (files && files.length > 0) {
          await handleFiles(files);
        }
        fileInput.value = '';
      });
    }

    // File preview modal close
    document.querySelectorAll('#filePreviewModal .modal-close, #filePreviewModal .modal-cancel').forEach(el => {
      el.addEventListener('click', () => closeModal('filePreviewModal'));
    });

    // Delete file from preview
    const deleteBtn = document.getElementById('deleteFileBtn');
    if (deleteBtn) {
      deleteBtn.addEventListener('click', async () => {
        const fileId = deleteBtn.dataset.fileId;
        if (fileId && confirm('Delete this file?')) {
          await SuzumeFiles.remove(parseInt(fileId));
          closeModal('filePreviewModal');
          renderFiles();
          showToast('File deleted');
        }
      });
    }
  }

  async function handleFiles(fileList) {
    const files = Array.from(fileList);
    showToast(`Processing ${files.length} file(s)...`);
    
    const results = await SuzumeFiles.uploadMultiple(files);
    
    if (results.length > 0) {
      showToast(`Successfully uploaded ${results.length} file(s) 📁`);
      renderFiles();
      await refreshDashboard();
    } else {
      showToast('No files were uploaded', 'error');
    }
  }

  function renderFiles() {
    const grid = document.getElementById('fileGrid');
    const countEl = document.getElementById('fileCount');
    const sizeEl = document.getElementById('fileTotalSize');

    const files = SuzumeFiles.getAll();

    // Update stats
    if (countEl) countEl.textContent = files.length;
    if (sizeEl) sizeEl.textContent = SuzumeFiles.formatSize(SuzumeFiles.getTotalSize());

    if (!grid) return;

    if (files.length === 0) {
      grid.innerHTML = `
        <div class="memory-empty" style="grid-column:1/-1">
          <div class="empty-icon">📁</div>
          <p>No files yet</p>
          <p class="empty-sub">Upload files for Suzume to read and remember</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = files.map(f => `
      <div class="file-card glass" data-id="${f.id}">
        <div class="file-card-icon">${f.icon || '📄'}</div>
        <div class="file-card-name">${escapeHtml(f.name)}</div>
        <div class="file-card-size">${SuzumeFiles.formatSize(f.size)}</div>
      </div>
    `).join('');

    // Click to preview
    grid.querySelectorAll('.file-card').forEach(card => {
      card.addEventListener('click', () => {
        const id = parseInt(card.dataset.id);
        const file = files.find(f => f.id === id);
        if (file) showFilePreview(file);
      });
    });
  }

  function showFilePreview(file) {
    const modal = document.getElementById('filePreviewModal');
    const title = document.getElementById('filePreviewTitle');
    const content = document.getElementById('filePreviewContent');
    const info = document.getElementById('filePreviewInfo');
    const deleteBtn = document.getElementById('deleteFileBtn');

    if (!modal || !title || !content || !info) return;

    title.textContent = file.icon + ' ' + file.name;
    deleteBtn.dataset.fileId = file.id;

    // File content
    content.innerHTML = '';

    if (file.category === 'image' && file.dataUrl) {
      content.innerHTML = `<img src="${file.dataUrl}" alt="${file.name}" style="max-height:60vh;object-fit:contain">`;
    } else if (file.textContent) {
      content.innerHTML = `<div class="file-text-content">${escapeHtml(file.textContent)}</div>`;
    } else if (file.category === 'audio' && file.dataUrl) {
      content.innerHTML = `<audio controls style="width:100%"><source src="${file.dataUrl}"></audio>`;
    } else if (file.category === 'video' && file.dataUrl) {
      content.innerHTML = `<video controls style="width:100%;max-height:50vh"><source src="${file.dataUrl}"></video>`;
    } else {
      content.innerHTML = `<div style="text-align:center;padding:40px;color:var(--text-muted)">📄 Preview not available for this file type</div>`;
    }

    // File info
    info.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px;padding-top:16px;border-top:1px solid var(--border-color);font-size:0.82rem">
        <span style="color:var(--text-secondary)">Name:</span><span>${escapeHtml(file.name)}</span>
        <span style="color:var(--text-secondary)">Size:</span><span>${SuzumeFiles.formatSize(file.size)}</span>
        <span style="color:var(--text-secondary)">Type:</span><span>${file.type || 'Unknown'}</span>
        <span style="color:var(--text-secondary)">Uploaded:</span><span>${SuzumeFiles.formatDate(file.timestamp)}</span>
      </div>
    `;

    modal.classList.add('active');

    // Close on overlay click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal('filePreviewModal');
    });
  }

  // ===== SETTINGS =====
  function setupSettings() {
    // User name
    const nameInput = document.getElementById('settingsName');
    const saveNameBtn = document.getElementById('saveNameBtn');
    
    if (nameInput) nameInput.value = App.userName;
    
    if (saveNameBtn && nameInput) {
      saveNameBtn.addEventListener('click', async () => {
        const name = nameInput.value.trim();
        if (name) {
          App.userName = name;
          await SuzumeDB.setSetting('userName', name);
          showToast('Name updated!');
          refreshDashboard();
        }
      });
    }

    // Export data
    const exportBtn = document.getElementById('exportDataBtn');
    if (exportBtn) {
      exportBtn.addEventListener('click', async () => {
        try {
          const data = await SuzumeDB.exportAll();
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `suzume-backup-${new Date().toISOString().split('T')[0]}.json`;
          a.click();
          URL.revokeObjectURL(url);
          showToast('Data exported successfully! 📤');
        } catch (e) {
          showToast('Export failed', 'error');
        }
      });
    }

    // Import data
    const importBtn = document.getElementById('importDataBtn');
    const importInput = document.getElementById('importFileInput');
    if (importBtn && importInput) {
      importBtn.addEventListener('click', () => importInput.click());
      importInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
          const text = await file.text();
          const data = JSON.parse(text);
          await SuzumeDB.importAll(data);
          
          // Reload all data
          await SuzumeMemory.load();
          await SuzumeFiles.load();
          await refreshDashboard();
          renderMemory();
          renderFiles();
          
          showToast('Data imported successfully! 📥');
        } catch (e) {
          showToast('Import failed: invalid file', 'error');
        }
        importInput.value = '';
      });
    }

    // Clear data
    const clearBtn = document.getElementById('clearDataBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete ALL data? This cannot be undone!')) {
          if (confirm('Really? All your memories, files, and conversations will be permanently deleted.')) {
            await SuzumeDB.clearAll();
            await SuzumeMemory.load();
            await SuzumeFiles.load();
            await refreshDashboard();
            renderMemory();
            renderFiles();
            refreshChatHistory();
            showToast('All data cleared');
          }
        }
      });
    }

    // Update storage info
    updateStorageInfo();
  }

  async function updateStorageInfo() {
    try {
      const info = await SuzumeDB.getStorageInfo();
      const storageEl = document.getElementById('storageUsed');
      const barEl = document.getElementById('storageBar');

      if (storageEl) {
        storageEl.textContent = `${info.totalItems} items stored`;
      }

      // Estimate storage usage as a percentage (assuming ~50MB quota)
      if (barEl) {
        const percent = Math.min(100, (info.estimatedBytes / (50 * 1024 * 1024)) * 100);
        barEl.style.width = percent + '%';
      }
    } catch (e) {
      console.warn('Storage info error:', e);
    }
  }

  // ===== MODALS =====
  function setupModals() {
    // Close all modals on X or Cancel
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(el => {
      el.addEventListener('click', () => {
        const modal = el.closest('.modal-overlay');
        if (modal) modal.classList.remove('active');
      });
    });

    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
      });
    });

    // Quick note
    const quickNoteBtn = document.getElementById('btnAddNote');
    const quickNoteModal = document.getElementById('quickNoteModal');
    const saveQuickNoteBtn = document.getElementById('saveQuickNoteBtn');

    if (quickNoteBtn && quickNoteModal) {
      quickNoteBtn.addEventListener('click', () => quickNoteModal.classList.add('active'));
    }

    if (saveQuickNoteBtn) {
      saveQuickNoteBtn.addEventListener('click', async () => {
        const title = document.getElementById('quickNoteTitle').value.trim();
        const content = document.getElementById('quickNoteContent').value.trim();

        if (!title && !content) {
          showToast('Please enter a title or content', 'error');
          return;
        }

        await SuzumeMemory.addNote(title || 'Quick Note', content, ['quick']);
        showToast('Note saved! 📝');
        closeModal('quickNoteModal');
        document.getElementById('quickNoteTitle').value = '';
        document.getElementById('quickNoteContent').value = '';
        refreshDashboard();
      });
    }
  }

  function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('active');
  }

  // ===== SAKURA PARTICLE CANVAS =====
  function setupSakuraCanvas() {
    const canvas = document.getElementById('sakura-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let petals = [];
    let animId = null;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }

    function createPetals(count) {
      petals = [];
      for (let i = 0; i < count; i++) {
        petals.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height * -1,
          size: 4 + Math.random() * 10,
          speedY: 0.3 + Math.random() * 0.8,
          speedX: -0.2 + Math.random() * 0.4,
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: -0.02 + Math.random() * 0.04,
          opacity: 0.3 + Math.random() * 0.4,
          color: Math.random() > 0.5 ? '#FF6B9D' : '#FFB7C5'
        });
      }
    }

    function drawPetals() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      petals.forEach(p => {
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rotation);
        ctx.globalAlpha = p.opacity;
        ctx.fillStyle = p.color;

        // Draw sakura petal shape
        ctx.beginPath();
        ctx.moveTo(0, -p.size / 2);
        ctx.bezierCurveTo(
          p.size / 2, -p.size / 2,
          p.size / 2, p.size / 4,
          0, p.size / 2
        );
        ctx.bezierCurveTo(
          -p.size / 2, p.size / 4,
          -p.size / 2, -p.size / 2,
          0, -p.size / 2
        );
        ctx.fill();
        ctx.restore();

        // Update position
        p.y += p.speedY;
        p.x += p.speedX + Math.sin(p.y * 0.01) * 0.5;
        p.rotation += p.rotationSpeed;

        // Wrap around
        if (p.y > canvas.height + 20) {
          p.y = -20;
          p.x = Math.random() * canvas.width;
        }
        if (p.x > canvas.width + 20) p.x = -20;
        if (p.x < -20) p.x = canvas.width + 20;
      });

      animId = requestAnimationFrame(drawPetals);
    }

    resize();
    createPetals(Math.min(40, Math.floor(window.innerWidth / 30)));

    window.addEventListener('resize', () => {
      resize();
      createPetals(Math.min(40, Math.floor(window.innerWidth / 30)));
    });

    drawPetals();

    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
      if (animId) cancelAnimationFrame(animId);
    });
  }

  // ===== TOAST SYSTEM =====
  window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    
    if (type === 'error') {
      toast.style.borderLeft = '3px solid #F43F5E';
    } else {
      toast.style.borderLeft = '3px solid var(--accent-pink)';
    }

    container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) toast.remove();
    }, 3000);
  };

  // ===== UTILITY =====
  function formatTime(ts) {
    if (!ts) return '';
    const d = new Date(ts);
    const now = new Date();
    const diff = now - d;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
    if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
    if (diff < 604800000) return Math.floor(diff / 86400000) + 'd ago';
    return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ===== HANDLE URL HASH ON LOAD =====
  function handleInitialHash() {
    const hash = window.location.hash.replace('#', '');
    if (hash && ['home', 'chat', 'memory', 'files', 'settings'].includes(hash)) {
      switchView(hash);
    }
  }

  // ===== START =====
  document.addEventListener('DOMContentLoaded', () => {
    init();
    handleInitialHash();
  });

})();
