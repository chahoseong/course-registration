import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useEffect } from 'react';

export default function Login() {
  const { user, login, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/student');
      }
    }
  }, [user, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md text-center">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">수강신청 플랫폼</h1>
        <p className="text-gray-600 mb-8">계속하려면 Google 계정으로 로그인하세요</p>
        
        <button
          onClick={login}
          className="w-full flex items-center justify-center gap-3 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold py-3 px-4 rounded-lg transition-all duration-200"
        >
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" className="w-6 h-6" />
          <span>Google 계정으로 로그인</span>
        </button>
      </div>
    </div>
  );
}
