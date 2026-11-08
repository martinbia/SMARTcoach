/* MP4 blobs stay on this device. Never build a GitHub URL from a local filename. */
(() => {
  const normalName = name => name.normalize('NFC').toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '');
  async function access(mode, id, blob) {
    const db = await new Promise((resolve, reject) => {
      const request = indexedDB.open('smartcoach-local-videos', 1);
      request.onupgradeneeded = () => request.result.createObjectStore('files');
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    try {
      return await new Promise((resolve, reject) => {
        const tx = db.transaction('files', mode === 'read' || mode === 'keys' ? 'readonly' : 'readwrite');
        const store = tx.objectStore('files');
        const request = mode === 'keys' ? store.getAllKeys() : mode === 'read' ? store.get(id) : mode === 'remove' ? store.delete(id) : store.put(blob, id);
        tx.oncomplete = () => resolve(request.result);
        tx.onerror = () => reject(tx.error);
        tx.onabort = () => reject(tx.error);
      });
    } finally { db.close(); }
  }
  async function importFiles(files, catalogue) {
    const result = { imported: [], ignored: [], failed: [] };
    for (const file of files) {
      const video = catalogue.find(item => normalName(item.meta.Datei) === normalName(file.name));
      if (!video || !/\.mp4$/i.test(file.name)) { result.ignored.push(file.name); continue; }
      if (!file.size || file.size > 512 * 1024 * 1024 || (file.type && file.type !== 'video/mp4')) { result.failed.push(file.name); continue; }
      try { await access('write', video.id, file); result.imported.push(video.id); }
      catch { result.failed.push(file.name); }
    }
    return result;
  }
  window.SMART_VIDEOS = { access, importFiles, normalName };
})();
