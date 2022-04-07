import calendar
import datetime

import jwt
from flask import abort

from helpers.constants import JWT_SECRET, JWT_ALGORYTHM
from service.user import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def generate_tokens(self, username, password, is_refresh=False):
        user = self.user_service.get_by_username(username)

        if user is None:
            raise abort(404)

        if not is_refresh:
            if not self.user_service.compare_passwords(user.password, password):
                abort(400)

        data = {
            "username": user.username,
            "role": user.role
        }

        # access_token на 30 минут
        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        data["exp"] = calendar.timegm(min30.timetuple())
        access_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORYTHM)

        # refresh_token на 130 дней
        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORYTHM)

        tokens = {"access_token": access_token, "refresh_token": refresh_token}

        return tokens

    def approve_refresh_tokens(self, refresh_token):
        data = jwt.decode(refresh_token)
        username = data.get("username")
        return self.generate_tokens(username, None, is_refresh=True)
