import axios from 'axios';
import { auth } from '../firebase';
import type { Course } from '../types';

const api = axios.create();

api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getCourses = async (): Promise<Course[]> => {
  const response = await api.get('/api/courses');
  return response.data;
};

export const getCourse = async (id: string): Promise<Course> => {
    const response = await api.get(`/api/courses/${id}`);
    return response.data;
};

export const createCourse = async (course: Omit<Course, 'id' | 'current_count'>): Promise<Course> => {
  const response = await api.post('/api/courses', course);
  return response.data;
};

export const updateCourse = async (id: string, course: Partial<Course>): Promise<Course> => {
  const response = await api.put(`/api/courses/${id}`, course);
  return response.data;
};

export const deleteCourse = async (id: string): Promise<void> => {
  await api.delete(`/api/courses/${id}`);
};
