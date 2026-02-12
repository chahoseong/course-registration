import ChatWindow from '../components/ChatWindow';
import EnrollmentList from '../components/EnrollmentList';

export default function Student() {
  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-8rem)]">
      {/* Main Chat Area */}
      <div className="flex-1 flex justify-center">
        <ChatWindow />
      </div>

      {/* Sidebar - Enrollments */}
      <div className="w-full lg:w-80 flex-shrink-0">
         <EnrollmentList />
      </div>
    </div>
  );
}
