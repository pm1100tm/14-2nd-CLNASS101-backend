""" 유틸 모듈

    author: 심원두
    
    history:
        2021-01-19 - 리펙토링 (심원두)
"""
import jwt
import bcrypt
import re
import uuid
import time
import functools

from django.http import JsonResponse
from django.db import connection, reset_queries

from my_settings import SECRET_KEY, ALGORITHM, ENCODE
from user.models import User

def query_debugger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        number_of_start_queries = len(connection.queries)
        start                   = time.perf_counter()
        result                  = func(*args, **kwargs)
        end                     = time.perf_counter()
        number_of_end_queries   = len(connection.queries)
        
        print(f"-------------------------------------------------------------------")
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {number_of_end_queries-number_of_start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        print(f"-------------------------------------------------------------------")
        
        return result
    return wrapper

def login_decorator(login_required=False):
    def real_decorator(func):
        def wrapper(self, request, *args, **kwargs):
            try:
                access_token = request.headers.get('Authorization')
                
                if not access_token and not login_required:
                    request.user = User.objects.filter(id=0)
                    return func(self, request, *args, **kwargs)
                
                payload = jwt.decode(
                    access_token,
                    SECRET_KEY,
                    algorithm=ALGORITHM
                )
                
                user = User.objects.get(id=payload['user_id'])
                request.user = user
                
            except jwt.exceptions.DecodeError as e:
                return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
            
            except User.DoesNotExist:
                return JsonResponse({"message": "INVALID_USER"}, status=401)
            
            return func(self, request, *args, **kwargs)
        
        return wrapper
    return real_decorator

def get_hashed_pw(password):
    return bcrypt.hashpw(password.encode(ENCODE), bcrypt.gensalt()).decode(ENCODE)

def check_password(password, user_password):
    return bcrypt.checkpw(password.encode(ENCODE), user_password.encode(ENCODE))

def issue_access_token(user_id):
    return jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm=ALGORITHM)


class CommonUtil:
    """ 입력 체크 공통 부품 클래스

        Author : 심원두

        History:
            2021-01-19 - 초기 생성
    """
    @staticmethod
    def is_blank(*args):
        return all([value for value in args])
    
    @staticmethod
    def is_email_valid(email):
        """ 이메일 규칙
            - @ 앞은 이메일의 아이디에 해당하며 대소문자, 숫자, 특수문자(-_)를 사용할 수 있다.
            - @ 다음은 도메인이며 대소문자, 숫자로 이루어져 있다.
            - . 다음은 최상위 도메인이며 대소문자 숫자로 이루어진다.

            Author: 심원두

            History:
                2021-01-19(심원두): 초기생성
        """
        pattern = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email)
    
    @staticmethod
    def is_user_name_valid(user_name):
        """ 유저명 규칙
            - 한글만 입력 가능.
            - 최소 2자, 최대 25자

            Author: 심원두

            Parameter:
                user_name - 유저명(실명)

            History:
                2021-01-19(심원두): 초기생성
        """
        pattern = '^[가-힣]{2,25}$'
        return re.match(pattern, user_name)
    
    @staticmethod
    def is_valid_password(password):
        """ 비밀번호 규칙
            - 8자 이상, 25자 이하
            - 최소 하나 이상의 문자 및 하나 이상의 숫자

            Author : 심원두

            Parameter:
                password - 비밀번호

            History:
                2021-01-19(심원두): 초기생성
        """
        pattern = '^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        return re.match(pattern, password)
    
    @staticmethod
    def get_random_number():
        return str(uuid.uuid4())


class CommonConstant:
    NO_IMAGE_URL = 'no_image'
