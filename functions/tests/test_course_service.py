import pytest
from unittest.mock import MagicMock
from models.course import Course, CourseCreate
from services.course_service import CourseService

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def service(mock_repo):
    return CourseService(repo=mock_repo)

def test_get_all_courses(service, mock_repo):
    # Mock data
    mock_repo.list.return_value = [
        Course(id="1", title="C1", instructor="T1", max_students=10, current_count=0)
    ]

    courses = service.get_all_courses()
    
    assert len(courses) == 1
    assert courses[0].title == "C1"
    mock_repo.list.assert_called_once()

def test_get_course_by_id(service, mock_repo):
    mock_repo.get.return_value = Course(id="1", title="C1", instructor="T1", max_students=10, current_count=0)

    course = service.get_course("1")
    
    assert course is not None
    assert course.id == "1"
    mock_repo.get.assert_called_with("1")

def test_get_course_not_found(service, mock_repo):
    mock_repo.get.return_value = None

    course = service.get_course("999")
    
    assert course is None
    mock_repo.get.assert_called_with("999")

def test_create_course(service, mock_repo):
    course_data = CourseCreate(title="New", instructor="T", max_students=20)
    mock_repo.save.return_value = Course(id="new_id", **course_data.model_dump())

    created = service.create_course(course_data)
    
    assert created.id == "new_id"
    mock_repo.save.assert_called_once()

def test_delete_course(service, mock_repo):
    mock_repo.delete.return_value = True

    result = service.delete_course("1")
    
    assert result is True
    mock_repo.delete.assert_called_with("1")

