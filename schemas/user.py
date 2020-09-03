from ma import ma
from models.user import UserModel
from marshmallow import pre_dump


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "activated", "confirmation")
        load_instance = True
        include_relationships = True

    @pre_dump
    def _pre_dump(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user
