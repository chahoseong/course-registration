import pytest
from unittest.mock import MagicMock
from models.course import Course, CourseCreate
from repositories.firestore_repo import FirestoreCourseRepository

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def repo(mock_db):
    return FirestoreCourseRepository(db=mock_db)

def test_list_courses(repo, mock_db):
    # Mock data
    mock_doc = MagicMock()
    mock_doc.id = "course1"
    mock_doc.to_dict.return_value = {
        "title": "Test Course",
        "instructor": "Teacher",
        "max_students": 10,
        "current_count": 0
    }
    mock_db.collection.return_value.stream.return_value = [mock_doc]

    courses = repo.list()
    
    assert len(courses) == 1
    assert courses[0].id == "course1"
    assert courses[0].title == "Test Course"

def test_get_course(repo, mock_db):
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.id = "course1"
    mock_doc.to_dict.return_value = {
        "title": "Test Course",
        "instructor": "Teacher",
        "max_students": 10,
        "current_count": 0
    }
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    course = repo.get("course1")
    
    assert course is not None
    assert course.id == "course1"
    assert course.title == "Test Course"

def test_get_course_not_found(repo, mock_db):
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    course = repo.get("non-existent")
    
    assert course is None

def test_save_course_new(repo, mock_db):
    new_course = Course(id="", title="New", instructor="T", max_students=10)
    mock_db.collection.return_value.add.return_value = (None, MagicMock(id="new_id"))

    saved_course = repo.save(new_course)
    
    assert saved_course.id == "new_id"
    mock_db.collection.return_value.add.assert_called_once()

def test_save_course_existing(repo, mock_db):
    existing_course = Course(id="ext1", title="Existing", instructor="T", max_students=10)

    repo.save(existing_course)
    
    mock_db.collection.return_value.document.assert_called_with("ext1")
    mock_db.collection.return_value.document.return_value.set.assert_called_once()

def test_delete_course(repo, mock_db):
    repo.delete("course1")
    
    mock_db.collection.return_value.document.assert_called_with("course1")
    mock_db.collection.return_value.document.return_value.delete.assert_called_once()

