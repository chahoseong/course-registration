from typing import List, Optional
from google.cloud.firestore import FieldFilter
from repositories.base import BaseRepository
from models.course import Course
from models.user import User
from models.enrollment import Enrollment

class FirestoreCourseRepository(BaseRepository[Course]):
    def __init__(self, db):
        self.db = db
        self.collection = self.db.collection("courses")

    def list(self) -> List[Course]:
        docs = self.collection.stream()
        return [Course(id=doc.id, **doc.to_dict()) for doc in docs]

    def get(self, id: str) -> Optional[Course]:
        doc = self.collection.document(id).get()
        if doc.exists:
            return Course(id=doc.id, **doc.to_dict())
        return None

    def save(self, data: Course) -> Course:
        doc_data = data.model_dump(exclude={"id"})
        if data.id:
            self.collection.document(data.id).set(doc_data)
        else:
            _, doc_ref = self.collection.add(doc_data)
            data.id = doc_ref.id
        return data

    def delete(self, id: str) -> bool:
        self.collection.document(id).delete()
        return True

class FirestoreUserRepository(BaseRepository[User]):
    def __init__(self, db):
        self.db = db
        self.collection = self.db.collection("users")

    def list(self) -> List[User]:
        docs = self.collection.stream()
        return [User(**doc.to_dict()) for doc in docs]

    def get(self, uid: str) -> Optional[User]:
        doc = self.collection.document(uid).get()
        if doc.exists:
            return User(**doc.to_dict())
        return None

    def save(self, data: User) -> User:
        self.collection.document(data.uid).set(data.model_dump())
        return data

    def delete(self, uid: str) -> bool:
        self.collection.document(uid).delete()
        return True

class FirestoreEnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, db):
        self.db = db
        self.collection = self.db.collection("enrollments")

    def list(self) -> List[Enrollment]:
        docs = self.collection.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            if "id" in data:
                del data["id"]
            results.append(Enrollment(id=doc.id, **data))
        return results

    def get(self, id: str) -> Optional[Enrollment]:
        doc = self.collection.document(id).get()
        if doc.exists:
            data = doc.to_dict()
            if "id" in data:
                del data["id"]
            return Enrollment(id=doc.id, **data)
        return None

    def save(self, data: Enrollment) -> Enrollment:
        # id는 document key로 사용되므로 저장하지 않음 (중복 방지)
        self.collection.document(data.id).set(data.model_dump(exclude={"id"}))
        return data

    def delete(self, id: str) -> bool:
        self.collection.document(id).delete()
        return True

    def get_by_student_id(self, student_id: str) -> List[Enrollment]:
        # 'student_ids' 배열에 student_id가 포함된 문서 검색
        docs = self.collection.where(filter=FieldFilter("student_ids", "array_contains", student_id)).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            if "id" in data:
                del data["id"]
            results.append(Enrollment(id=doc.id, **data))
        return results
