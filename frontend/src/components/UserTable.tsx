import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { auth } from '../firebase';
import type { User } from '../types';
import { Shield, ShieldAlert, User as UserIcon } from 'lucide-react';


const getUsers = async (): Promise<User[]> => {
    const token = await auth.currentUser?.getIdToken();
    const response = await axios.get('/api/users', {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};

const updateUserRole = async ({ uid, role }: { uid: string, role: string }) => {
    const token = await auth.currentUser?.getIdToken();
    const response = await axios.put(`/api/users/${uid}/role?role=${role}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};

export default function UserTable() {
    const queryClient = useQueryClient();
    const { data: users, isLoading } = useQuery({ queryKey: ['users'], queryFn: getUsers });

    const mutation = useMutation({
        mutationFn: updateUserRole,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
        }
    });

    const toggleRole = (user: User) => {
        const newRole = user.role === 'admin' ? 'student' : 'admin';
        if (confirm(`${user.displayName}님의 권한을 ${newRole === 'admin' ? '관리자' : '학생'}으로 변경하시겠습니까?`)) {
            mutation.mutate({ uid: user.uid, role: newRole });
        }
    };

    if (isLoading) return <div className="text-center p-8">사용자 목록을 불러오는 중...</div>;

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">이름</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">이메일</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">현재 권한</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">권한 변경</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {users?.map((user) => (
                        <tr key={user.uid} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                    {user.photoURL ? (
                                        <img className="h-8 w-8 rounded-full mr-3" src={user.photoURL} alt="" />
                                    ) : (
                                        <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center mr-3">
                                            <UserIcon className="w-4 h-4 text-gray-500" />
                                        </div>
                                    )}
                                    <div className="text-sm font-medium text-gray-900">{user.displayName}</div>
                                </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                    user.role === 'admin' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                                }`}>
                                    {user.role === 'admin' ? '관리자' : '학생'}
                                </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <button
                                    onClick={() => toggleRole(user)}
                                    className="text-indigo-600 hover:text-indigo-900 p-2 rounded-lg hover:bg-indigo-50"
                                    title={user.role === 'admin' ? '학생으로 변경' : '관리자로 변경'}
                                >
                                    {user.role === 'admin' ? <ShieldAlert className="w-5 h-5" /> : <Shield className="w-5 h-5" />}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
