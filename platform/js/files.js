/**
 * SUZUME FILE PROCESSOR
 * Handles file uploads, preview, and content extraction
 * All files are stored in IndexedDB for Suzume's memory
 */

const SuzumeFiles = (function() {
  let files = [];
  let loaded = false;

  const FILE_TYPES = {
    image: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'],
    document: ['txt', 'md', 'json', 'csv', 'xml', 'html', 'css', 'js', 'ts', 'py', 'java', 'cpp', 'c', 'h', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'log'],
    audio: ['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'wma'],
    video: ['mp4', 'webm', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
    archive: ['zip', 'rar', 'tar', 'gz', '7z'],
    pdf: ['pdf'],
    other: []
  };

  /**
   * Load all stored files
   */
  async function load() {
    try {
      files = await SuzumeDB.getFiles();
      files.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
      loaded = true;
      return files;
    } catch (e) {
      console.error('Files load error:', e);
      files = [];
      loaded = true;
      return files;
    }
  }

  /**
   * Get file category from extension
   */
  function getFileCategory(ext) {
    ext = ext.toLowerCase().replace(/^\./, '');
    for (const [category, extensions] of Object.entries(FILE_TYPES)) {
      if (extensions.includes(ext)) return category;
    }
    return 'other';
  }

  /**
   * Get icon for file type
   */
  function getFileIcon(type, ext) {
    const cat = getFileCategory(ext);
    const icons = {
      image: '🖼️',
      document: '📄',
      audio: '🎵',
      video: '🎬',
      archive: '📦',
      pdf: '📕',
      other: '📎'
    };
    return icons[cat] || '📄';
  }

  /**
   * Read file as ArrayBuffer
   */
  function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);
      reader.readAsArrayBuffer(file);
    });
  }

  /**
   * Read file as text
   */
  function readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file);
    });
  }

  /**
   * Read file as Data URL
   */
  function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(file);
    });
  }

  /**
   * Upload and store a file
   */
  async function upload(file) {
    const ext = file.name.split('.').pop() || '';
    const category = getFileCategory(ext);
    const icon = getFileIcon(category, ext);

    let dataUrl = '';
    let textContent = '';

    try {
      // For images, store as data URL for preview
      if (category === 'image') {
        dataUrl = await readFileAsDataURL(file);
      }
      // For text documents, extract text content
      else if (category === 'document' || category === 'pdf') {
        textContent = await readFileAsText(file);
      }
      // For audio/video, store as data URL
      else if (category === 'audio' || category === 'video') {
        dataUrl = await readFileAsDataURL(file);
      }
    } catch (e) {
      console.warn('Could not read file content:', e.message);
    }

    const fileEntry = {
      name: file.name,
      size: file.size,
      type: file.type,
      category: category,
      extension: ext,
      icon: icon,
      dataUrl: dataUrl,
      textContent: textContent,
      timestamp: Date.now()
    };

    try {
      const id = await SuzumeDB.addFile(fileEntry);
      fileEntry.id = id;
      files.unshift(fileEntry);

      // Also add to memory for knowledge base
      await SuzumeMemory.add(
        'file',
        file.name,
        textContent ? textContent.substring(0, 500) : `File: ${file.name} (${formatSize(file.size)})`,
        '',
        [category, ext]
      );

      // Log activity
      await SuzumeMemory.logActivity('📁', `Uploaded file: "${file.name}"`);

      return fileEntry;
    } catch (e) {
      console.error('File upload error:', e);
      throw e;
    }
  }

  /**
   * Upload multiple files
   */
  async function uploadMultiple(fileList) {
    const results = [];
    for (const file of fileList) {
      try {
        const result = await upload(file);
        results.push(result);
      } catch (e) {
        console.warn('Failed to upload:', file.name, e.message);
      }
    }
    return results;
  }

  /**
   * Delete a file
   */
  async function remove(id) {
    try {
      await SuzumeDB.deleteFile(id);
      files = files.filter(f => f.id !== id);
      return true;
    } catch (e) {
      console.error('File delete error:', e);
      return false;
    }
  }

  /**
   * Get all files
   */
  function getAll() {
    return [...files];
  }

  /**
   * Get files by category
   */
  function getByCategory(category) {
    return files.filter(f => f.category === category);
  }

  /**
   * Format file size
   */
  function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  /**
   * Format timestamp
   */
  function formatDate(ts) {
    if (!ts) return '';
    const d = new Date(ts);
    const now = new Date();
    const diff = now - d;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
    if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
    if (diff < 604800000) return Math.floor(diff / 86400000) + 'd ago';

    return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  /**
   * Get total storage size
   */
  function getTotalSize() {
    return files.reduce((sum, f) => sum + (f.size || 0), 0);
  }

  // Public API
  return {
    load,
    upload,
    uploadMultiple,
    remove,
    getAll,
    getByCategory,
    getFileCategory,
    getFileIcon,
    formatSize,
    formatDate,
    getTotalSize
  };
})();

window.SuzumeFiles = SuzumeFiles;
