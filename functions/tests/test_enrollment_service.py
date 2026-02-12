import pytest
from datetime import datetime
from unittest.mock import MagicMock
from models.course import Course
from models.enrollment import Enrollment, EnrollmentCreate
from services.enrollment_service import EnrollmentService, EnrollmentError

@pytest.fixture
def mock_course_repo():
    return MagicMock()

@pytest.fixture
def mock_enroll_repo():
    return MagicMock()

@pytest.fixture
def service(mock_course_repo, mock_enroll_repo):
    return EnrollmentService(course_repo=mock_course_repo, enroll_repo=mock_enroll_repo)

def test_enroll_success(service, mock_course_repo, mock_enroll_repo):
    # Mock course
    course_id = "c1"
    student_id = "s1"
    mock_course = Course(id=course_id, title="C1", instructor="T1", max_students=10, current_count=5)
    mock_course_repo.get.return_value = mock_course
    mock_enroll_repo.get.return_value = None # Not enrolled yet

    result = service.enroll_student(student_id, course_id)
    
    assert result.course_id == course_id
    assert result.student_id == student_id
    mock_course_repo.save.assert_called_once()
    assert mock_course.current_count == 6

def test_enroll_full_fails(service, mock_course_repo, mock_enroll_repo):
    course_id = "c1"
    student_id = "s1"
    mock_course = Course(id=course_id, title="C1", instructor="T1", max_students=10, current_count=10)
    mock_course_repo.get.return_value = mock_course
    mock_enroll_repo.get.return_value = None

    with pytest.raises(EnrollmentError, match="Course is full"):
        service.enroll_student(student_id, course_id)

def test_enroll_duplicate_fails(service, mock_course_repo, mock_enroll_repo):
    course_id = "c1"
    student_id = "s1"
    mock_course = Course(id=course_id, title="C1", instructor="T1", max_students=10, current_count=5)
    mock_course_repo.get.return_value = mock_course
    mock_enroll_repo.get.return_value = Enrollment(id="s1_c1", student_id=student_id, course_id=course_id, timestamp=datetime.now())

    with pytest.raises(EnrollmentError, match="Already enrolled"):
        service.enroll_student(student_id, course_id)

def test_enroll_course_not_found(service, mock_course_repo, mock_enroll_repo):
    course_id = "non-existent"
    student_id = "s1"
    mock_course_repo.get.return_value = None

    with pytest.raises(EnrollmentError, match="Course not found"):
        service.enroll_student(student_id, course_id)

