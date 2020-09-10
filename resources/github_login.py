from flask import g
from flask_restful import Resource
from oa import github
from models.user import UserModel
from flask_jwt_extended import create_access_token, create_refresh_token


class GithubLogin(Resource):
    @classmethod
    def get(cls):
        return github.authorize(
            callback="http://localhost:5000/login/github/authorized"
        )


class GithubAuthorize(Resource):
    @classmethod
    def get(cls):
        resp = github.authorized_response()
        g.access_token = resp["access_token"]
        github_user = github.get("user")
        github_username = github_user.data["login"]
        github_email = github_user.data["email"]
        user = UserModel.find_by_username(github_username)
        if not user:
            user = UserModel(username=github_username, password=None, email=github_email)
            user.save_to_db()
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token }