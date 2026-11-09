/* Independent local WAV copies keyed by stable dialogue-step ID. */
(() => {
  'use strict';
  const DB_NAME = 'smartcoach-prompt-audio';
  const STORE = 'files';
  const MAX_SIZE = 64 * 1024 * 1024;
  let allowedIds = new Set();
  let configured = false;
  let resolveCatalogue;
  let rejectCatalogue;
  const catalogueReady = new Promise((resolve, reject) => { resolveCatalogue = resolve; rejectCatalogue = reject; });
  catalogueReady.catch(() => {});
  const session = new Map();
  const validId = id => configured && allowedIds.has(id);

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
    await catalogueReady;
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
    await catalogueReady;
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
    await catalogueReady;
    let stored = [];
    try { stored = await access('keys'); }
    catch (error) { if (!session.size) throw error; }
    return [...new Set([...stored, ...session.keys()])].filter(validId);
  }

  async function remove(id) {
    await catalogueReady;
    if (!validId(id)) throw new Error('Für diese Dialogzeile ist keine WAV-Zuordnung freigegeben.');
    const sessionOnly = session.get(id)?.persistent === false;
    try { await access('remove', id); }
    catch (error) { if (!sessionOnly) throw error; }
    session.delete(id);
  }

  function configure(dialogues) {
    if (!Array.isArray(dialogues) || !dialogues.length) throw new Error('Der Ansprache-Katalog ist nicht gültig.');
    const nextAllowed = new Set();
    const allIds = new Set();
    for (const dialogue of dialogues) {
      if (!dialogue || !/^[A-Z]$/.test(dialogue.id || '') || !Array.isArray(dialogue.steps) || !dialogue.steps.length)
        throw new Error('Der Ansprache-Katalog ist nicht gültig.');
      for (const [index, step] of dialogue.steps.entries()) {
        if (!step || step.id !== `${dialogue.id}${index + 1}` || allIds.has(step.id)
          || !['SMARTcoach', 'Patient'].includes(step.speaker) || !String(step.text || '').trim()
          || typeof step.locked !== 'boolean' || step.approved !== !step.locked)
          throw new Error('Der Ansprache-Katalog ist nicht gültig.');
        allIds.add(step.id);
        if (step.approved) nextAllowed.add(step.id);
      }
    }
    allowedIds = nextAllowed;
    configured = true;
    resolveCatalogue();
  }

  function rejectConfiguration(error) {
    if (!configured) rejectCatalogue(error || new Error('Der Ansprache-Katalog konnte nicht validiert werden.'));
  }

  window.SMART_PROMPT_AUDIO = { configure, rejectConfiguration, choose, get, keys, remove, sessionInfo: id => session.get(id), isAllowed: validId, maxSize: MAX_SIZE };
})();
