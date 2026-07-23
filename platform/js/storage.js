/**
 * SUZUME STORAGE ENGINE
 * Personal Data Network — IndexedDB powered persistent storage
 * All data belongs to Suzume's shared memory system
 */

const SuzumeDB = (function() {
  const DB_NAME = 'SuzumePlatform';
  const DB_VERSION = 2;

  let db = null;
  let ready = false;
  const readyCallbacks = [];

  /**
   * Open database connection
   */
  async function open() {
    return new Promise((resolve, reject) => {
      if (ready && db) {
        resolve(db);
        return;
      }

      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = function(e) {
        const database = e.target.result;

        // Messages store (chat history)
        if (!database.objectStoreNames.contains('messages')) {
          const msgStore = database.createObjectStore('messages', { keyPath: 'id', autoIncrement: true });
          msgStore.createIndex('timestamp', 'timestamp', { unique: false });
          msgStore.createIndex('conversation', 'conversationId', { unique: false });
        }

        // Memory store (notes, links, knowledge)
        if (!database.objectStoreNames.contains('memory')) {
          const memStore = database.createObjectStore('memory', { keyPath: 'id', autoIncrement: true });
          memStore.createIndex('type', 'type', { unique: false });
          memStore.createIndex('timestamp', 'timestamp', { unique: false });
          memStore.createIndex('tags', 'tags', { unique: false, multiEntry: true });
        }

        // Files store
        if (!database.objectStoreNames.contains('files')) {
          const fileStore = database.createObjectStore('files', { keyPath: 'id', autoIncrement: true });
          fileStore.createIndex('timestamp', 'timestamp', { unique: false });
          fileStore.createIndex('type', 'type', { unique: false });
          fileStore.createIndex('name', 'name', { unique: false });
        }

        // Activity store
        if (!database.objectStoreNames.contains('activity')) {
          const actStore = database.createObjectStore('activity', { keyPath: 'id', autoIncrement: true });
          actStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // Settings store
        if (!database.objectStoreNames.contains('settings')) {
          database.createObjectStore('settings', { keyPath: 'key' });
        }

        // Conversations store
        if (!database.objectStoreNames.contains('conversations')) {
          const convStore = database.createObjectStore('conversations', { keyPath: 'id', autoIncrement: true });
          convStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };

      request.onsuccess = function(e) {
        db = e.target.result;
        ready = true;

        // Handle connection close (e.g., in private browsing)
        db.onclose = function() {
          ready = false;
          db = null;
        };
        db.onversionchange = function() {
          db.close();
          ready = false;
          db = null;
        };

        readyCallbacks.forEach(cb => cb());
        readyCallbacks.length = 0;
        resolve(db);
      };

      request.onerror = function(e) {
        reject(new Error('Database error: ' + e.target.error?.message));
      };
    });
  }

  /**
   * Wait for database to be ready
   */
  async function ready() {
    if (ready) return;
    return new Promise(resolve => {
      readyCallbacks.push(resolve);
    });
  }

  /**
   * Generic add to store
   */
  async function add(storeName, data) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const request = store.add(data);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Generic put (update) in store
   */
  async function put(storeName, data) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const request = store.put(data);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Generic get by id
   */
  async function get(storeName, id) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const request = store.get(id);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Generic get all from store
   */
  async function getAll(storeName) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all by index
   */
  async function getAllByIndex(storeName, indexName, value) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const index = store.index(indexName);
      const request = index.getAll(value);
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Delete by id
   */
  async function remove(storeName, id) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Clear entire store
   */
  async function clear(storeName) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Count items in store
   */
  async function count(storeName) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const request = store.count();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Search memory by text in title and content
   */
  async function searchMemory(query) {
    const all = await getAll('memory');
    const q = query.toLowerCase();
    return all.filter(item =>
      (item.title && item.title.toLowerCase().includes(q)) ||
      (item.content && item.content.toLowerCase().includes(q)) ||
      (item.tags && item.tags.some(t => t.toLowerCase().includes(q)))
    ).sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * Get setting value
   */
  async function getSetting(key) {
    await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('settings', 'readonly');
      const store = tx.objectStore('settings');
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result ? request.result.value : null);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Set setting value
   */
  async function setSetting(key, value) {
    await open();
    return put('settings', { key, value, updated: Date.now() });
  }

  /**
   * Export all data as JSON
   */
  async function exportAll() {
    const data = {
      version: 2,
      exported: Date.now(),
      messages: await getAll('messages'),
      memory: await getAll('memory'),
      files: await getAll('files'),
      activity: await getAll('activity'),
      settings: await getAll('settings'),
      conversations: await getAll('conversations')
    };
    return data;
  }

  /**
   * Import data from JSON
   */
  async function importAll(data) {
    if (!data || !data.version) throw new Error('Invalid data format');

    // Clear existing
    await clear('messages');
    await clear('memory');
    await clear('files');
    await clear('activity');
    await clear('conversations');

    // Import each store
    const stores = ['messages', 'memory', 'files', 'activity', 'conversations'];
    for (const store of stores) {
      if (data[store] && Array.isArray(data[store])) {
        for (const item of data[store]) {
          // Remove old ids to get new ones
          delete item.id;
          await add(store, item);
        }
      }
    }

    // Import settings
    if (data.settings && Array.isArray(data.settings)) {
      for (const setting of data.settings) {
        await put('settings', setting);
      }
    }

    return true;
  }

  /**
   * Get storage usage estimate
   */
  async function getStorageInfo() {
    const stores = ['messages', 'memory', 'files', 'activity', 'conversations'];
    const info = {};
    let totalItems = 0;

    for (const store of stores) {
      const count = await count(store);
      info[store] = count;
      totalItems += count;
    }

    let estimatedBytes = 0;
    try {
      if (navigator.storage && navigator.storage.estimate) {
        const estimate = await navigator.storage.estimate();
        estimatedBytes = estimate.usage || 0;
      }
    } catch(e) { /* ignore */ }

    return {
      stores: info,
      totalItems,
      estimatedBytes,
      estimatedFormatted: formatBytes(estimatedBytes)
    };
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  // Public API
  return {
    open,
    ready,
    add,
    put,
    get,
    getAll,
    getAllByIndex,
    remove,
    clear,
    count,
    searchMemory,
    getSetting,
    setSetting,
    exportAll,
    importAll,
    getStorageInfo,
    // Convenience aliases
    addMessage: (msg) => add('messages', { ...msg, timestamp: Date.now() }),
    getMessages: () => getAllByIndex('messages', 'timestamp'),
    addMemory: (mem) => add('memory', { ...mem, timestamp: Date.now() }),
    getMemories: () => getAllByIndex('memory', 'timestamp'),
    addFile: (file) => add('files', { ...file, timestamp: Date.now() }),
    getFiles: () => getAllByIndex('files', 'timestamp'),
    addActivity: (act) => add('activity', { ...act, timestamp: Date.now() }),
    getActivity: () => getAllByIndex('activity', 'timestamp'),
    deleteMessage: (id) => remove('messages', id),
    deleteMemory: (id) => remove('memory', id),
    deleteFile: (id) => remove('files', id),
    clearMessages: () => clear('messages'),
    clearAll: async () => {
      await clear('messages');
      await clear('memory');
      await clear('files');
      await clear('activity');
      await clear('conversations');
    }
  };
})();

// Legacy support
window.SuzumeDB = SuzumeDB;
