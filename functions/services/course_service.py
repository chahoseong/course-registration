from typing import List, Optional
from models.course import Course, CourseCreate
from repositories.base import BaseRepository

class CourseService:
    def __init__(self, repo: BaseRepository[Course]):
        self.repo = repo

    def get_all_courses(self) -> List[Course]:
        return self.repo.list()

    def get_course(self, id: str) -> Optional[Course]:
        return self.repo.get(id)

    def create_course(self, course_data: CourseCreate) -> Course:
        # CourseCreate를 Course 모델로 변환 (ID는 저장 시 생성됨)
        new_course = Course(
            id="", # Repository에서 생성 예정
            **course_data.model_dump()
        )
        return self.repo.save(new_course)

    def delete_course(self, id: str) -> bool:
        return self.repo.delete(id)
