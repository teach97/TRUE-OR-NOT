export const STORAGE_CONSENT_KEY = 'ton_storage_consent';
const STORAGE_CONSENT_VERSION = '2026-10-05-v1';

export function readStorageConsent(): boolean {
  try {return localStorage.getItem(STORAGE_CONSENT_KEY) === STORAGE_CONSENT_VERSION;}
  catch {return false;}
}

export function writeStorageConsent(enabled: boolean): boolean {
  try {
    if (enabled) localStorage.setItem(STORAGE_CONSENT_KEY, STORAGE_CONSENT_VERSION);
    else localStorage.removeItem(STORAGE_CONSENT_KEY);
    return true;
  } catch {return false;}
}
