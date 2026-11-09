/* Independent local WAV copies keyed by stable dialogue-step ID. */
(() => {
  'use strict';
  const DB_NAME = 'smartcoach-prompt-audio';
  const STORE = 'files';
  const MAX_SIZE = 64 * 1024 * 1024;
  let lockedIds = new Set(['D5']);
  const session = new Map();
  const validId = id => /^[A-Z]\d+$/.test(id || '') && !lockedIds.has(id);

  function access(mode, id, value) {
    return new Promise((resolve, reject) => {
      if (!('indexedDB' in window)) { reject(new Error('Der lokale Audiospeicher ist nicht verfügbar.')); return; }
      const request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = () => request.result.createObjectStore(STORE);
      request.onerror = () => reject(request.error || new Error('Der lokale Audiospeicher ist nicht verfügbar.'));
      request.onsuccess = () => {
        const db = request.result;
        const finish = callback => { db.close(); callback(); };
        try {
          const transaction = db.transaction(STORE, mode === 'read' || mode === 'keys' ? 'readonly' : 'readwrite');
          const store = transaction.objectStore(STORE);
          const operation = mode === 'keys' ? store.getAllKeys()
            : mode === 'read' ? store.get(id)
              : mode === 'remove' ? store.delete(id) : store.put(value, id);
          let result;
          operation.onsuccess = () => { result = operation.result; };
          transaction.oncomplete = () => finish(() => resolve(result));
          operation.onerror = () => finish(() => reject(operation.error || transaction.error));
          transaction.onabort = () => finish(() => reject(transaction.error || new Error('Der lokale Audiospeicher ist nicht verfügbar.')));
        } catch (error) { finish(() => reject(error)); }
      };
    });
  }

  async function prepare(file) {
    if (!/\.wav$/i.test(file?.name || '') || !file.size || file.size > MAX_SIZE)
      throw new Error('Bitte eine WAV-Datei mit höchstens 64 MB auswählen.');
    const bytes = await file.arrayBuffer();
    if (bytes.byteLength !== file.size) throw new Error('Die ausgewählte Datei konnte nicht vollständig gelesen werden.');
    const signature = new Uint8Array(bytes, 0, Math.min(bytes.byteLength, 12));
    const ascii = offset => String.fromCharCode(...signature.slice(offset, offset + 4));
    if (signature.byteLength < 12 || ascii(0) !== 'RIFF' || ascii(8) !== 'WAVE')
      throw new Error('Die Datei enthält keinen lesbaren RIFF/WAVE-Header.');
    return new Blob([bytes], { type: 'audio/wav' });
  }

  async function choose(file, id) {
    if (!validId(id)) throw new Error('Für diese Dialogzeile ist keine WAV-Zuordnung freigegeben.');
    const record = { blob: await prepare(file), name: file.name, persistent: false };
    session.set(id, record);
    try {
      await access('write', id, record);
      record.persistent = true;
    } catch { /* Make the session-only state visible; never claim persistence. */ }
    return record;
  }

  async function get(id) {
    if (!validId(id)) return null;
    if (session.has(id)) return session.get(id);
    const record = await access('read', id);
    if (!record) return null;
    if (!(record.blob instanceof Blob)) throw new Error('Die gespeicherte WAV-Datei ist unvollständig.');
    await record.blob.slice(0, 12).arrayBuffer();
    record.persistent = true;
    session.set(id, record);
    return record;
  }

  async function keys() {
    let stored = [];
    try { stored = await access('keys'); }
    catch (error) { if (!session.size) throw error; }
    return [...new Set([...stored, ...session.keys()])].filter(validId);
  }

  async function remove(id) {
    const sessionOnly = session.get(id)?.persistent === false;
    try { await access('remove', id); }
    catch (error) { if (!sessionOnly) throw error; }
    session.delete(id);
  }

  function configure(dialogues) {
    lockedIds = new Set(dialogues.flatMap(dialogue => dialogue.steps.filter(step => step.locked).map(step => step.id)));
  }

  window.SMART_PROMPT_AUDIO = { configure, choose, get, keys, remove, sessionInfo: id => session.get(id), isAllowed: validId, maxSize: MAX_SIZE };
})();
