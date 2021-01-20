""" 사용자 정의 예외 클래스
    
    Author : 심원두
    
    History :
        2021-01-19 - 초기 생성(심원두)
"""

"""User APP"""
class BlankField(Exception):
    def __init__(self):
        super().__init__('INPUT_REQUIRED')


class NotValidUserName(Exception):
    def __init__(self):
        super().__init__('INVALID_USER_NAME')


class NotValidEmail(Exception):
    def __init__(self):
        super().__init__('INVALID_EMAIL_FORMAT')


class NotValidPassword(Exception):
    def __init__(self):
        super().__init__('INVALID_PASSWORD_FORMAT')


class DuplicatedUser(Exception):
    def __init__(self):
        super().__init__('DUPLICATED_USER')


class NotExistUser(Exception):
    def __init__(self):
        super().__init__('NOT_EXIST_USER')


class WrongPassword(Exception):
    def __init__(self):
        super().__init__('WRONG_PASSWORD')