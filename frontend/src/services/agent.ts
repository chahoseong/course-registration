import axios from 'axios';
import { auth } from '../firebase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'; // Adjust as needed

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const sendMessageToAgent = async (message: string): Promise<string> => {
  try {
    const response = await api.post('/api/agent/chat', { message });
    return response.data.response;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};
