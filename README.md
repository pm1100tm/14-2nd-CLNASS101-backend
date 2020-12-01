# CLNASS101 Project

<a href="https://ibb.co/1ZcRcyj"><img src="https://i.ibb.co/BLkTkWF/logo-text.png" alt="logo-text" border="0"></a>

<br>

## 프로젝트 개요

#### 1. 개발 기간 : 2020년 11월 30일 (월) ~ 12월 11일 (금), 12일간 진행

#### 2. 개발 인원
- Frontend : 안상혁, 박영준, 안혜수
- Backend : 김민구(PM), 심원두, 신재훈

#### 3. 목적
* 클래스101 사이드의 디자인과 기능을 채용하여 모델링 및 기능 설계/구현
* **`Django ORM`** 에 대한 심화 학습 적용
* RESTful API 설계
* **`git rebase`** 기능 사용하여 commit message 관리 

#### 4. Reference
- ***[클래스101 사이트 보러가기](https://class101.net/)***
- ***[모델링 보러가기](https://aquerytool.com:443/aquerymain/index/?rurl=af077285-3c15-4bd8-84ab-3e6acd5c63aa
)*** - ***password : 251cs7*** 
- ***[API Documentation 보러가기 (준비 중)]()***

<br>

## 핵심 기능 Key Feature
- 김민구
    - creator.FirstTemporaryView 강의 개설 첫 번째 단계
    - creator.SecondTemporaryView 강의 개설 두 번째 단계
    - creator.ThirdTemporaryView 강의 개설 세 번째 단계
    - creator.FourthTemporaryView 강의 개설 네 번째 단계
    
- 심원두
    - product.ProductDetailView 강의 디테일
    - ClassDetailView
    - LectureDetailView
    - order.SelectProductAndPaymentView
    - order.OrderProductView
    
- 신재훈
    - user.SignUpView 회원가입
    - user.LogInView 로그인
    - user.KakaoLogInView 소셜로그인
    - user.SearchView 검색
    - user.MyPageView 마이페이지
    - product.MainPageView 전체 강의 리스트
    - product.CommunityView 강의 내의 게시물
    - product.CommunityCommentView 강의 내의 게시물 댓글
    - product.LectureCommentView 강의 댓글
    - product.CommunityLikeView 강의 내의 게시물 좋아요
    - product.ProductLikeView 강의 좋아요

<br>

## Refactoring Plan (~2021-01-31)
* CommonUtils
- [x] 프로젝트 전체 - 상수 파일 생성
- [x] 프로젝트 전체 - 공통 입력 체크 생성
- [x] 프로젝트 전체 - 에러 메세지 통합 관리
 
* User App
- [x] ~~user.SignUpView (회원가입)~~
- [x] ~~user.SignInView (로그인)~~
- [ ] user.SocialSignInView (소셜 로그인 - 카카오)
- [ ] user.MyPageView (마이 페이지)
- [ ] user.UpdateUserInfoView (유저 정보 수정)

* Product App
- [ ] product.MainPageView (메인 페이지)
- [ ] product.ProductDetailView (강의 Preview)
- [ ] product.ClassDetailView (구매한 강의 내용 디테일)
- [ ] product.LectureDetailView (구매한 강의 디테일 - 영상 정보)
- [ ] product.order.SelectProductAndPaymentView (결제 전 페이지)
- [ ] product.order.OrderProductView (결제)

## License
**모든 사진은 저작권이 없는 사진을 사용했습니다.**
