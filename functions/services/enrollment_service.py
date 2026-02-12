from datetime import datetime
from typing import Optional
from models.course import Course
from models.enrollment import Enrollment
from repositories.base import BaseRepository

class EnrollmentError(Exception):
    pass

class EnrollmentService:
    def __init__(self, course_repo: BaseRepository[Course], enroll_repo: BaseRepository[Enrollment]):
        self.course_repo = course_repo
        self.enroll_repo = enroll_repo

    def enroll_student(self, student_id: str, course_id: str) -> Enrollment:
        # 1. 강의 존재 확인
        course = self.course_repo.get(course_id)
        if not course:
            raise EnrollmentError("Course not found")

        # 2. 중복 신청 확인
        enrollment_id = f"{student_id}_{course_id}"
        if self.enroll_repo.get(enrollment_id):
            raise EnrollmentError("Already enrolled in this course")

        # 3. 정원 확인
        if course.current_count >= course.max_students:
            raise EnrollmentError("Course is full")

        # 4. 신청 내역 생성 및 저장
        new_enrollment = Enrollment(
            id=enrollment_id,
            student_id=student_id,
            course_id=course_id,
            timestamp=datetime.now()
        )
        self.enroll_repo.save(new_enrollment)

        # 5. 강의 인원 업데이트
        course.current_count += 1
        self.course_repo.save(course)

        return new_enrollment
