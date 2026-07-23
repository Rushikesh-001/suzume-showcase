/**
 * SUZUME MEMORY SYSTEM
 * Shared knowledge base — notes, links, and indexed content
 * The UI and system share this memory seamlessly
 */

const SuzumeMemory = (function() {
  let memories = [];
  let loaded = false;

  /**
   * Load all memories from storage
   */
  async function load() {
    try {
      memories = await SuzumeDB.getMemories();
      // Sort by timestamp descending (newest first)
      memories.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
      loaded = true;
      return memories;
    } catch (e) {
      console.error('Memory load error:', e);
      memories = [];
      loaded = true;
      return memories;
    }
  }

  /**
   * Add a memory item
   */
  async function add(type, title, content, url, tags) {
    const memory = {
      type: type, // 'note' | 'link' | 'file'
      title: title || 'Untitled',
      content: content || '',
      url: url || '',
      tags: tags || [],
      timestamp: Date.now()
    };

    try {
      const id = await SuzumeDB.addMemory(memory);
      memory.id = id;
      memories.unshift(memory);

      // Log activity
      await logActivity(
        type === 'note' ? '📝' : type === 'link' ? '🔗' : '📁',
        `Saved ${type}: "${title || 'Untitled'}"`
      );

      return memory;
    } catch (e) {
      console.error('Memory add error:', e);
      throw e;
    }
  }

  /**
   * Add a note
   */
  async function addNote(title, content, tags) {
    return add('note', title, content, '', tags);
  }

  /**
   * Add a link
   */
  async function addLink(title, url, tags) {
    return add('link', title, '', url, tags);
  }

  /**
   * Delete a memory
   */
  async function remove(id) {
    try {
      await SuzumeDB.deleteMemory(id);
      memories = memories.filter(m => m.id !== id);
      return true;
    } catch (e) {
      console.error('Memory delete error:', e);
      return false;
    }
  }

  /**
   * Search through all memories
   */
  function search(query) {
    if (!query || !query.trim()) return memories;
    const q = query.toLowerCase().trim();
    return memories.filter(m =>
      (m.title && m.title.toLowerCase().includes(q)) ||
      (m.content && m.content.toLowerCase().includes(q)) ||
      (m.tags && m.tags.some(t => t.toLowerCase().includes(q)))
    );
  }

  /**
   * Filter by type
   */
  function filterByType(type) {
    if (type === 'all') return memories;
    return memories.filter(m => m.type === type);
  }

  /**
   * Get all memories
   */
  function getAll() {
    return [...memories];
  }

  /**
   * Log an activity entry
   */
  async function logActivity(icon, text) {
    try {
      await SuzumeDB.addActivity({ icon, text });
    } catch (e) {
      // Silent fail for activity logging
    }
  }

  // Public API
  return {
    load,
    add,
    addNote,
    addLink,
    remove,
    search,
    filterByType,
    getAll,
    logActivity
  };
})();

window.SuzumeMemory = SuzumeMemory;
