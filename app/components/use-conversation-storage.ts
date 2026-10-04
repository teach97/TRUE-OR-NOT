'use client';
import {useEffect,useReducer,useState} from 'react';
import {conversationClient} from './conversation-client';
import {ConversationStorage} from './conversation-storage';
export function useConversationStorage(){
  const [,render]=useReducer((value:number)=>value+1,0);
  const [storage]=useState(()=>new ConversationStorage(conversationClient,render));
  useEffect(()=>{void storage.refresh();return()=>storage.invalidate();},[storage]);
  return storage;
}
