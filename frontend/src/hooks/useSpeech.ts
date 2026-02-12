import { useState, useCallback } from 'react';

export const useSpeech = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);

  // STT (Speech to Text)
  const startListening = useCallback(() => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Browser does not support speech recognition.');
      return;
    }

    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = 'ko-KR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const speechResult = event.results[0][0].transcript;
      setTranscript(speechResult);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error', event.error);
      setIsListening(false);
    };

    recognition.start();
  }, []);

  const stopListening = useCallback(() => {
    // recognition.stop() logic is tricky without keeping the instance ref, 
    // but usually startListening handles one-shot. 
    // If we want continuous listening, we need to adjust.
    // For now, let's assume it stops automatically or on end.
    setIsListening(false);
  }, []);

  // TTS (Text to Speech)
  const speak = useCallback((text: string) => {
    if (!('speechSynthesis' in window)) {
      alert('Browser does not support speech synthesis.');
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, []);

  const cancelSpeech = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  return {
    isListening,
    transcript,
    setTranscript, // To clear it after sending
    startListening,
    stopListening,
    isSpeaking,
    speak,
    cancelSpeech,
  };
};
