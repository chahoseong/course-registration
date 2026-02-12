import { useState } from 'react';
import CourseTable from '../components/CourseTable';
import UserTable from '../components/UserTable';
import AdminStats from '../components/AdminStats';
import { BookOpen, Users } from 'lucide-react';

export default function Admin() {
  const [activeTab, setActiveTab] = useState<'courses' | 'users'>('courses');

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">관리자 대시보드</h1>
          <p className="mt-1 text-sm text-gray-500">강의 정보를 등록하고 학생 및 수강 현황을 관리합니다.</p>
        </div>
        
        {/* Tabs */}
        <div className="flex bg-white p-1 rounded-lg shadow-sm border border-gray-100 self-start">
          <button
            onClick={() => setActiveTab('courses')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'courses' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <BookOpen className="w-4 h-4" /> 강의 관리
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'users' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="w-4 h-4" /> 유저 관리
          </button>
        </div>
      </div>

      <AdminStats />

      {activeTab === 'courses' ? <CourseTable /> : <UserTable />}
    </div>
  );
}
