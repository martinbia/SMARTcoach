/* MP4 blobs stay on this device. Never build a GitHub URL from a local filename. */
(() => {
  const normalName = name => name.replace(/\s*\(\d+\)(?=\.mp4$)/i, '').normalize('NFC').toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '');
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
  const selected = new Map();
  async function copyFile(file) {
    if (!/\.mp4$/i.test(file.name || '') || !file.size || file.size > 512 * 1024 * 1024) throw new Error('Bitte eine MP4-Datei mit höchstens 512 MB auswählen.');
    // Android document providers can return generic MIME types and temporary File
    // references. Store independent bytes, never a reference to the picker URI.
    const bytes = await file.arrayBuffer();
    if (bytes.byteLength !== file.size) throw new Error('Die ausgewählte Datei konnte nicht vollständig gelesen werden.');
    return new Blob([bytes], { type: 'video/mp4' });
  }
  async function choose(file, id) {
    const record = { blob: await copyFile(file), name: file.name, persistent: false };
    selected.set(id, record);
    try {
      await access('write', id, { blob: record.blob, name: record.name });
      record.persistent = true;
    } catch { /* Playback must still work when quota or storage is unavailable. */ }
    return record;
  }
  async function get(id) {
    if (selected.has(id)) return selected.get(id);
    const stored = await access('read', id);
    if (!stored) return null;
    let record;
    if (stored instanceof Blob) {
      // Migrate the old File-based representation, where possible, by reading
      // the bytes while the reference is still valid.
      const bytes = await stored.arrayBuffer();
      record = { blob: new Blob([bytes], { type: 'video/mp4' }), name: stored.name || '', persistent: false };
      try { await access('write', id, { blob: record.blob, name: record.name }); record.persistent = true; } catch { /* session copy remains usable */ }
    } else if (stored.blob instanceof Blob) {
      // Fail here with a readable message if an existing copy is unreadable.
      await stored.blob.slice(0, 32).arrayBuffer();
      record = { blob: stored.blob, name: stored.name || '', persistent: true };
    } else throw new Error('Die gespeicherte Filmdatei ist unvollständig.');
    selected.set(id, record);
    return record;
  }
  async function keys() {
    let stored = [];
    try { stored = await access('keys'); }
    catch { if (!selected.size) throw new Error('Der lokale Videospeicher ist nicht verfügbar.'); }
    return [...new Set([...stored, ...selected.keys()])];
  }
  async function remove(id) {
    const sessionOnly = selected.get(id)?.persistent === false;
    try { await access('remove', id); }
    catch { if (!sessionOnly) throw new Error('Die gespeicherte Kopie konnte nicht entfernt werden.'); }
    selected.delete(id);
  }
  async function importFiles(files, catalogue) {
    const result = { imported: [], temporary: [], ignored: [], failed: [] };
    for (const file of files) {
      const video = catalogue.find(item => normalName(item.meta.Datei) === normalName(file.name));
      if (!video) { result.ignored.push(file.name); continue; }
      try {
        const record = await choose(file, video.id);
        (record.persistent ? result.imported : result.temporary).push(video.id);
      } catch { result.failed.push(file.name); }
    }
    return result;
  }
  window.SMART_VIDEOS = { access, importFiles, normalName, choose, get, keys, remove,
    sessionInfo: id => selected.get(id) };
})();
