"""
This module contains a class to satisfy user requirements
"""
import subprocess
import ollama
from app.exceptions.exception_handling import UnexpectedError, NotFoundException
from app.db.init_db import AureliusDB
from app.schemas.schemas import UserSetup


class UserService:
    """
    This class contains all method to create, get and update user
    Alongside with methods to verify ollama installation and available models
    """

    def __init__(self):
        self.database = AureliusDB()

    def is_ollama_installed(self):
        """
        This method verifies id ollama is installed on the user's machine

        :param self: Description
        """

        try:
            subprocess.check_output(
                ["ollama", "--version"], stderr=subprocess.STDOUT)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False
        except OSError:
            return False

    def retrieve_ollama_models_list(self):
        """
        This method retrieves the available local models from ollama

        :param self: Description
        """
        try:
            model_list = ollama.list()
            available_models = []
            for model in model_list.get('models', []):
                print(model)
                model_info = ollama.show(model.get('model'))
                template = model_info.get('template', '')
                if 'tool' in template.lower() or 'function' in template.lower():
                    available_models.append(dict(model))
            return available_models
        except Exception as e:
            raise UnexpectedError(
                f"An error occurred while retrieving ollama models {e}") from e

    def is_user_regitered(self):
        """
        This method verifies is user is already registered

        :param self: Description
        """
        user_name = self.database.is_user_registerd()
        if user_name is None:
            return False
        return True

    def register_user(self, user: UserSetup):
        """
        This method creates the user for the local database

        :param self: Description
        :param user: Description
        :type user: UserSetup
        """
        try:
            self.database.register_user(user.user_name, user.model)
        except Exception as e:
            raise UnexpectedError(
                f"An error occurred while user registration {e}") from e

    def update_user_info(self, user: UserSetup):
        """
        This method updates user local database info

        :param self: Description
        :param user: Description
        :type user: UserSetup
        """
        try:
            self.database.update_user_data(user.user_name, user.model)
        except Exception as e:
            raise UnexpectedError(
                f"An error occurred while updating data {e}") from e

    def get_user_data(self):
        """
        This method gets local user data
        """

        if not self.is_user_regitered():
            raise NotFoundException("User not found")

        data = self.database.get_user_data()
        return data
