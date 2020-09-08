from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import os

from libs import image_helper
from libs.strings import gettext
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        """
        Used to upload an image file.
        It uses JWT to retrieve user information and then saves the image to the user's folder
        If there's a filename conflict, it appends a number at the end
        """
        data = image_schema.load(request.files)  # { image: FileStorage }
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"  # static/images/user_1
        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {"message": gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return (
                {"message": gettext("image_illegal_extension").format(extension)},
                400,
            )


class Image(Resource):
    @jwt_required
    def get(self, filename: str):
        """Returns the requested image in the user's folder only"""
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("illegal_filename").format(filename)}
        try:
            print(image_helper.get_path(filename, folder=folder))
            return send_file(image_helper.get_path(filename, folder=folder)) # No se pone 200 porque tira un error
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404

    @jwt_required
    def delete(self, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("illegal_filename").format(filename)}
        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"message": gettext("image_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404
        except:
            traceback.print_exc()
            return {"message": gettext("image_delete_failed").format(filename)}, 500
