import { useEffect, useState } from 'react';
import { collection, query, where, onSnapshot, getDoc, doc } from 'firebase/firestore';
import { db } from '../firebase';
import { useAuth } from '../hooks/useAuth';
import type { Enrollment, Course } from '../types';
import { Calendar, Clock, BookOpen } from 'lucide-react';

interface EnrollmentWithCourse extends Enrollment {
  course?: Course;
}

export default function EnrollmentList() {
  const { user } = useAuth();
  const [enrollments, setEnrollments] = useState<EnrollmentWithCourse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    const q = query(collection(db, 'enrollments'), where('student_id', '==', user.uid));
    
    const unsubscribe = onSnapshot(q, async (snapshot) => {
      const enrollmentData: EnrollmentWithCourse[] = [];
      
      for (const docSnapshot of snapshot.docs) {
        const data = docSnapshot.data() as Enrollment;
        // Fetch course details
        try {
          const courseDocRef = doc(db, 'courses', data.course_id);
          const courseDoc = await getDoc(courseDocRef);
          if (courseDoc.exists()) {
             enrollmentData.push({ ...data, id: docSnapshot.id, course: { id: courseDoc.id, ...courseDoc.data() } as Course });
          } else {
             enrollmentData.push({ ...data, id: docSnapshot.id });
          }
        } catch (e) {
          console.error("Error fetching course for enrollment", data.course_id, e);
          enrollmentData.push({ ...data, id: docSnapshot.id });
        }
      }

      setEnrollments(enrollmentData);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [user]);

  if (loading) {
    return <div className="p-4 text-center text-gray-500">수강 내역을 불러오는 중...</div>;
  }

  if (enrollments.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
        <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-gray-900">신청 내역 없음</h3>
        <p className="text-gray-500 text-sm">에이전트에게 수강 신청을 요청해보세요!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
        <BookOpen className="w-5 h-5 text-blue-600" />
        나의 수강 내역
      </h2>
      <div className="grid gap-4">
        {enrollments.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
             <div className="flex justify-between items-start">
               <div>
                 <h3 className="font-semibold text-gray-900">{item.course?.title || 'Unknown Course'}</h3>
                 <p className="text-sm text-gray-600 bg-gray-100 inline-block px-2 py-0.5 rounded mt-1">
                   {item.course?.instructor || 'Unknown Instructor'}
                 </p>
               </div>
               <span className="text-xs text-gray-400 flex items-center gap-1">
                 <Clock className="w-3 h-3" />
                 {new Date(item.timestamp).toLocaleDateString()}
               </span>
             </div>
             {item.course?.start_time && item.course?.end_time && (
                <div className="mt-3 text-sm text-gray-500 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {item.course.start_time} - {item.course.end_time}
                </div>
             )}
          </div>
        ))}
      </div>
    </div>
  );
}
