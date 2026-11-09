/* A user-selected demonstration image, stored only in this browser. */
(() => {
  async function access(mode, value) {
    const db = await new Promise((resolve, reject) => {
      const request = indexedDB.open('smartcoach-demo-xray', 1);
      request.onupgradeneeded = () => request.result.createObjectStore('images');
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    try {
      return await new Promise((resolve, reject) => {
        const tx = db.transaction('images', mode === 'read' ? 'readonly' : 'readwrite');
        const store = tx.objectStore('images');
        const request = mode === 'read' ? store.get('demo') : mode === 'remove' ? store.delete('demo') : store.put(value, 'demo');
        tx.oncomplete = () => resolve(request.result);
        tx.onerror = () => reject(tx.error);
        tx.onabort = () => reject(tx.error);
      });
    } finally { db.close(); }
  }
  async function prepare(file) {
    const extension = (file.name || '').split('.').pop().toLowerCase();
    const type = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp' }[extension];
    if (!type || !file.size || file.size > 12 * 1024 * 1024) throw new Error('Bitte ein Demo-Bild als JPG, PNG oder WebP mit höchstens 12 MB auswählen.');
    const blob = new Blob([await file.arrayBuffer()], { type });
    let bitmap;
    try { bitmap = await createImageBitmap(blob); }
    catch { throw new Error('Das ausgewählte Bild kann nicht gelesen werden. Bitte eine andere Bilddatei auswählen.'); }
    bitmap.close();
    return { blob, name: file.name };
  }
  window.SMART_XRAY = { access, prepare };
})();
