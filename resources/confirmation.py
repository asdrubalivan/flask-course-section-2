import traceback
from time import time
from flask import make_response, render_template
from flask_restful import Resource

from libs.mailgun import MailgunException
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

confirmation_schema = ConfirmationSchema()

NOT_FOUND = "Confirmation reference not found"
EXPIRED = "The link has expired"
ALREADY_CONFIRMED = "Registration has been already confirmed"
USER_NOT_FOUND = "User not found"
RESEND_SUCCESSFUL = "New confirmation sent"
RESEND_FAIL = "Resend confirmation fail"


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Returns confirmation HTML page"""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404
        if confirmation.expired:
            return {"message": EXPIRED}, 400
        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()
        headers = {"Content-Type": "application/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """Returns list of confirmation for a given user, just for testing"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(Confirmation.expire_at)
                ],
            },
            200,
        )

    @classmethod
    def post(cls, user_id: int):
        """Resends confirmation email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": RESEND_SUCCESSFUL}, 201
        except MailgunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": RESEND_FAIL}, 500
