from typing import List, Optional
from models.user import User
from repositories.base import BaseRepository

class UserService:
    def __init__(self, repo: BaseRepository[User]):
        self.repo = repo

    def get_all_users(self) -> List[User]:
        return self.repo.list()

    def get_user(self, uid: str) -> Optional[User]:
        return self.repo.get(uid)

    def update_user_role(self, uid: str, role: str) -> Optional[User]:
        user = self.repo.get(uid)
        if user:
            user.role = role
            return self.repo.save(user)
        return None
