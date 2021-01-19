""" 사용자 정의 예외 클래스
    
    Author : 심원두
    
    History :
        2021-01-19 - 초기 생성(심원두)
"""

"""User APP"""
class BlankField(Exception):
    def __init__(self):
        super().__init__('필수 입력 값이 입력되지 않았습니다.')


class NotValidUserName(Exception):
    def __init__(self):
        super().__init__('올바른 유저명이 아닙니다.')


class NotValidEmail(Exception):
    def __init__(self):
        super().__init__('올바른 이메일 형식이 아닙니다.')


class NotValidPassword(Exception):
    def __init__(self):
        super().__init__('올바른 비밀번호 형식이 아닙니다.')


class DuplicateUser(Exception):
    def __init__(self):
        super().__init__('이미 가입되어 있는 회원입니다.')