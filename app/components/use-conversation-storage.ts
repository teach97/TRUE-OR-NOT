'use client';
import {useEffect,useReducer,useState} from 'react';
import {conversationClient} from './conversation-client';
import {ConversationStorage} from './conversation-storage';
import {readStorageConsent,STORAGE_CONSENT_KEY} from './conversation-consent';
export function useConversationStorage(){
  const [,render]=useReducer((value:number)=>value+1,0);
  const [storage]=useState(()=>new ConversationStorage(conversationClient,render));
  useEffect(()=>{
    const syncConsent=()=>{const value=readStorageConsent();if(storage.consent!==value)storage.setConsent(value);};
    syncConsent();
    void storage.refresh();
    const onStorage=(event:StorageEvent)=>{if(event.key===STORAGE_CONSENT_KEY||event.key===null)syncConsent();};
    window.addEventListener('storage',onStorage);
    return()=>{window.removeEventListener('storage',onStorage);storage.invalidate();};
  },[storage]);
  return storage;
}
