from typing import List
from models.course import Course
from repositories.base import BaseRepository

class AgentService:
    def __init__(self, course_repo: BaseRepository[Course]):
        self.course_repo = course_repo

    def chat(self, user_id: str, message: str) -> str:
        # 간단한 의도 분석 및 답변 생성 로직
        # 실제로는 여기서 LLM(Gemini 등)을 호출해야 함
        
        courses = self.course_repo.list()
        
        if "강의" in message or "과목" in message or "목록" in message:
            if not courses:
                return "현재 등록된 강의가 없습니다."
            
            response = "현재 수강 가능한 강의 목록입니다:\n\n"
            for course in courses:
                time_str = f"{course.start_time} - {course.end_time}" if course.start_time and course.end_time else "시간 미정"
                response += f"- **{course.title}** ({course.instructor}): {time_str}\n"
            return response
        
        if "안녕" in message:
            return "안녕하세요! 수강 신청 도우미입니다. 궁금하신 강의 정보나 수강 신청 방법에 대해 물어보세요."
            
        return "죄송합니다. 아직 학습 중인 기능입니다. 강의 목록을 확인하시려면 '강의 목록 보여줘'라고 입력해 보세요."
