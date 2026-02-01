from fastapi import Request
from typing import Optional, List

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request

        self.email: Optional[str] = None
        self.password: Optional[str] = None

        self.errors: List[str] = []

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")
        self.password = form.get("password")

    async def is_valid(self) -> bool:
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 1:
            self.errors.append("A valid password is required")
        if not self.errors:
            print('is valid')
            return True
        print('is not valid')
        return False
