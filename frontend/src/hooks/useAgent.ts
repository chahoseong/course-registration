import { useState, useCallback } from 'react';
import type { Message } from '../types/chat';
import { sendMessageToAgent } from '../services/agent';

export const useAgent = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const sendMessage = useCallback(async (text: string) => {
    console.log('[useAgent] sendMessage start', { text });
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      const responseText = await sendMessageToAgent(text);
      console.log('[useAgent] sendMessage success', { responseText });
      
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        text: responseText,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error('[useAgent] sendMessage failed', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        text: 'Sorry, I encountered an error matching your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  return { messages, isProcessing, sendMessage };
};
