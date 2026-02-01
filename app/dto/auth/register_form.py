from fastapi import Request
from typing import Optional, List

class RegisterForm:
    def __init__(self, request: Request):
        self.request: Request = request

        # поля, как в форме
        self.name: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.confirm_password: Optional[str] = None
        self.terms: Optional[str] = None

        self.errors: List[str] = []

    async def load_data(self):
        form = await self.request.form()

        # html → python
        self.name = form.get("name")
        self.email = form.get("email")
        self.password = form.get("password")
        self.confirm_password = form.get("confirm-password")
        self.terms = form.get("terms")

    async def is_valid(self) -> bool:
        if not self.name or len(self.name.strip()) == 0:
            self.errors.append("Имя обязательно.")

        if not self.email or "@" not in self.email:
            self.errors.append("Нужен корректный email.")

        if not self.password or len(self.password) < 1:
            self.errors.append("Пароль обязателен.")

        if self.password != self.confirm_password:
            self.errors.append("Пароли не совпадают.")

        if not self.terms:
            self.errors.append("Для регистрации нужно согласиться с условиями.")

        return not self.errors
