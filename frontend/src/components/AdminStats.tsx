import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { auth } from '../firebase';
import { Users, BookOpen, UserCheck, TrendingUp } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const getStats = async () => {
    const token = await auth.currentUser?.getIdToken();
    const response = await axios.get(`${API_URL}/api/stats`, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};

export default function AdminStats() {
    const { data: stats, isLoading } = useQuery({ queryKey: ['admin-stats'], queryFn: getStats });

    if (isLoading) return <div className="animate-pulse flex space-x-4"><div className="flex-1 space-y-4 py-1">...</div></div>;

    const cards = [
        { title: '전체 강의', value: stats?.total_courses, icon: BookOpen, color: 'bg-blue-500' },
        { title: '등록 학생', value: stats?.total_students, icon: Users, color: 'bg-green-500' },
        { title: '총 수강 신청', value: stats?.total_enrollments, icon: UserCheck, color: 'bg-purple-500' },
        { title: '신청률', value: `${((stats?.total_enrollments / (stats?.total_courses * 30)) * 100 || 0).toFixed(1)}%`, icon: TrendingUp, color: 'bg-orange-500' },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {cards.map((card) => (
                <div key={card.title} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                    <div className={`${card.color} p-3 rounded-lg text-white`}>
                        <card.icon className="w-6 h-6" />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">{card.title}</p>
                        <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                    </div>
                </div>
            ))}
        </div>
    );
}
