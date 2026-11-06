/* The selected photo stays in this browser's IndexedDB. No upload or remote URL. */
window.SMART_IDLE_IMAGE = {
  async access(mode, blob) {
    const db = await new Promise((resolve, reject) => {
      const request = indexedDB.open('smartcoach-local-media', 1);
      request.onupgradeneeded = () => request.result.createObjectStore('images');
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    try {
      return await new Promise((resolve, reject) => {
        const tx = db.transaction('images', mode === 'read' ? 'readonly' : 'readwrite');
        const store = tx.objectStore('images');
        const request = mode === 'read' ? store.get('idle')
          : mode === 'remove' ? store.delete('idle') : store.put(blob, 'idle');
        tx.oncomplete = () => resolve(request.result);
        tx.onerror = () => reject(tx.error);
        tx.onabort = () => reject(tx.error);
      });
    } finally { db.close(); }
  },
  async validate(file) {
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      throw new Error('Bitte ein Foto als JPG, PNG oder WebP auswählen.');
    }
    if (file.size > 12 * 1024 * 1024) throw new Error('Bitte ein Bild mit höchstens 12 MB auswählen.');
    let bitmap;
    try { bitmap = await createImageBitmap(file); }
    catch { throw new Error('Dieses Bild konnte nicht geöffnet werden. Bitte ein anderes Foto auswählen.'); }
    bitmap.close();
  }
};
