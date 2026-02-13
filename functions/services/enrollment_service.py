from datetime import datetime
from typing import Optional, List
from models.course import Course
from models.enrollment import Enrollment
from repositories.base import BaseRepository

class EnrollmentError(Exception):
    pass

class EnrollmentService:
    def __init__(self, course_repo: BaseRepository[Course], enroll_repo: BaseRepository[Enrollment]):
        self.course_repo = course_repo
        self.enroll_repo = enroll_repo

    def get_student_enrollments(self, student_id: str) -> List[Enrollment]:
        # Repository capability check
        if hasattr(self.enroll_repo, 'get_by_student_id'):
            return self.enroll_repo.get_by_student_id(student_id)
        return []

    def enroll_student(self, student_id: str, course_id: str) -> Enrollment:
        print(f"Enroll Service: Enrolling student {student_id} to course {course_id}")
        
        # 1. 강의 존재 확인
        course = self.course_repo.get(course_id)
        if not course:
            raise EnrollmentError("Course not found")

        # 2. 해당 강의의 수강 신청 문서(하나)를 가져온다 (ID = course_id)
        enrollment = self.enroll_repo.get(course_id)
        
        if not enrollment:
            # 아직 신청자가 없으면 새로 생성
            enrollment = Enrollment(
                id=course_id,
                course_id=course_id,
                student_ids=[],
                timestamp=datetime.now()
            )

        # 3. 중복 신청 확인
        if student_id in enrollment.student_ids:
            raise EnrollmentError("Already enrolled in this course")

        # 4. 정원 확인 (현재 인원수 체크는 Course 모델의 current_count 사용)
        if course.current_count >= course.max_students:
            raise EnrollmentError("Course is full")

        # 5. 학생 추가 및 저장
        enrollment.student_ids.append(student_id)
        # timestamp 업데이트 (선택 사항, 마지막 신청 시간 등)
        enrollment.timestamp = datetime.now()
        
        self.enroll_repo.save(enrollment)

        # 6. 강의 인원 업데이트
        course.current_count = len(enrollment.student_ids) # 정확성을 위해 리스트 길이로 갱신
        self.course_repo.save(course)

        return enrollment

    def cancel_enrollment(self, student_id: str, course_id: str) -> Enrollment:
        print(f"Enroll Service: Canceling enrollment for student {student_id} from course {course_id}")
        
        # 1. 강의 존재 확인
        course = self.course_repo.get(course_id)
        if not course:
            raise EnrollmentError("Course not found")

        # 2. 수강 신청 문서 확인
        enrollment = self.enroll_repo.get(course_id)
        if not enrollment or student_id not in enrollment.student_ids:
            raise EnrollmentError("Not enrolled in this course")

        # 3. 학생 제거 및 저장
        enrollment.student_ids.remove(student_id)
        self.enroll_repo.save(enrollment)

        # 4. 강의 인원 업데이트
        course.current_count = len(enrollment.student_ids) 
        self.course_repo.save(course)

        return enrollment
