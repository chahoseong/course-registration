export interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  role: 'student' | 'admin';
}

export interface Course {
  id: string;
  title: string;
  instructor: string;
  max_students: number;
  current_count: number;
  start_time?: string;
  end_time?: string;
  description?: string;
}

export interface Enrollment {
  id: string;
  student_id: string;
  course_id: string;
  timestamp: string; // ISO string
}
