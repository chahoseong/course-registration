import axios from 'axios';
import { auth } from '../firebase';

const api = axios.create();

api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  console.log('[agent-api] request interceptor', {
    url: config.url,
    method: config.method,
    hasUser: !!user,
  });
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
    console.log('[agent-api] auth header attached', {
      uid: user.uid,
      tokenLength: token.length,
    });
  }
  return config;
});

export const sendMessageToAgent = async (message: string): Promise<string> => {
  try {
    console.log('[agent-api] POST /api/agent/chat', { message });
    const response = await api.post('/api/agent/chat', { message });
    console.log('[agent-api] response received', {
      status: response.status,
      data: response.data,
    });
    return response.data.response;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error sending message:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
    } else {
      console.error('Error sending message:', error);
    }
    throw error;
  }
};
