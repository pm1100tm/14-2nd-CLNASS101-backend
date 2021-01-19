"""
공통 입력 체크 모듈
"""
import re


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
        regex   = re.compile(pattern)
        
        return regex.match(email.strip())

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
        regex = re.compile(pattern)
        
        return regex.match(password.strip())