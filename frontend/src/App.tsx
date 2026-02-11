import { useState, useEffect } from 'react';
import { 
  signInWithPopup, 
  GoogleAuthProvider, 
  onAuthStateChanged, 
  signOut,
  type User 
} from 'firebase/auth';
import { auth } from './firebase';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleLogin = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error("Login failed:", error);
      alert("로그인에 실패했습니다.");
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const testBackend = async () => {
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      alert(JSON.stringify(data));
    } catch (error) {
      console.error("Backend test failed:", error);
      alert("백엔드 통신에 실패했습니다.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-xl font-semibold">로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center">
        <h1 className="text-3xl font-bold text-blue-600 mb-6">
          수강신청 AI 에이전트
        </h1>
        
        {user ? (
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-gray-700">
                환영합니다, <span className="font-bold text-blue-800">{user.displayName}</span>님!
              </p>
              <p className="text-sm text-gray-500">{user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition"
            >
              로그아웃
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">
              AI 에이전트 기반 수강신청 플랫폼에 오신 것을 환영합니다.
            </p>
            <button
              onClick={handleLogin}
              className="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-semibold py-2 px-4 rounded-lg transition shadow-sm"
            >
              <img 
                src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" 
                alt="Google" 
                className="w-5 h-5"
              />
              Google로 로그인
            </button>
          </div>
        )}

        <hr className="my-8 border-gray-200" />

        <div className="space-y-4">
          <p className="text-sm text-gray-500 font-medium">시스템 테스트</p>
          <button
            onClick={testBackend}
            className="w-full bg-gray-800 hover:bg-black text-white font-bold py-2 px-4 rounded-lg transition"
          >
            백엔드 헬스체크 (/api/health)
          </button>
        </div>
      </div>
      
      <footer className="mt-8 text-gray-400 text-sm">
        &copy; 2026 AI Course Registration Project
      </footer>
    </div>
  );
}

export default App;
