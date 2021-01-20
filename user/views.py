import json
import requests
from datetime            import datetime, timedelta

from django.db.models    import Count, Q
from django.views        import View
from django.http         import JsonResponse

from core.common_utils   import (
    CommonUtil,
    CommonConstant,
    login_decorator,
    query_debugger,
    get_hashed_pw,
    check_password,
    issue_access_token
)
from core.exception      import (
    NotValidEmail,
    NotValidUserName,
    NotValidPassword,
    DuplicatedUser,
    BlankField,
    NotExistUser,
    WrongPassword
)
from clnass_101.settings import S3_BUCKET_URL
from user.models         import (
    User,
    ProductLike,
    RecentlyView,
    UserProduct
)
from product.models      import (
    Product,
    Community,
    CommunityLike,
    CommunityComment,
    Lecture,
    LectureComment
)


class SignUpView(View):
    """ 회원가입 View
        
        Author : 심원두
        
        History :
            2021-01-19 - 리펙토링 (심원두)
    """
    @query_debugger
    def post(self, request):
        """ 회원 가입
            
            Author: 심원두
            
            Request:
                name     - 사용자 이름(실명)
                email    - 사용자 이메일
                password - 비밀번호
            
            Return:
                {"message": "SIGN_UP_SUCCESS"},         status=201 - 유저 정보 등록 성공
                {"message": "KEY_ERROR:{key_name}"},    status=400 - 키 에러
                {"message": "INPUT_REQUIRED"},          status=400 - 필수 입력 값 없음
                {"message": "INVALID_USER_NAME"},       status=400 - 잘못된 사용자 이름
                {"message": "INVALID_EMAIL_FORMAT"},    status=400 - 잘못된 이메일 형식
                {"message": "INVALID_PASSWORD_FORMAT"}, status=400 - 잘못된 비밀번호 형식
                {"message": "DUPLICATED_USER"},         status=400 - 중복된 유저 정보
                
            History :
                2021-01-19 - 리펙토링 완료 (심원두)
        """
        try:
            payload   = json.loads(request.body)
            
            user_name = payload["name"].strip()
            email     = payload["email"].strip()
            password  = payload["password"].strip()
            
            if not CommonUtil.is_blank(user_name, email, password):
                raise BlankField
            
            if not CommonUtil.is_user_name_valid(user_name):
                raise NotValidUserName
            
            if not CommonUtil.is_email_valid(email):
                raise NotValidEmail
            
            if not CommonUtil.is_valid_password(password):
                raise NotValidPassword
            
            if User.objects.filter(email=email, is_deleted=0).exists():
                raise DuplicatedUser
            
            User.objects.create(
                name     = user_name,
                email    = email,
                password = get_hashed_pw(password)
            )
            
            return JsonResponse({"message": "SIGN_UP_SUCCESS"}, status=201)
        
        except KeyError as e:
            return JsonResponse({"message": f"KEY_ERROR:{e}"}, status=400)
        
        except BlankField as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except NotValidUserName as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except NotValidEmail as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except NotValidPassword as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except DuplicatedUser as e:
            return JsonResponse({"message": f"{e}"}, status=400)


class SignInView(View):
    """ 로그인 View

        Author : 심원두

        History :
            2021-01-19 - 리텍토링 (심원두)
    """
    @query_debugger
    def post(self, request):
        """ 로그인
            
            Author: 심원두
            
            Request:
                email    - 사용자 이메일
                password - 비밀번호
            
            Return:
                {"message": "SIGN_IN_SUCCESS"},         status=200 - 유저 정보 등록 성공
                {"message": "KEY_ERROR:{key_name}"},    status=400 - 키 에러
                {"message": "INPUT_REQUIRED"},          status=400 - 필수 입력 값 없음
                {"message": "NOT_EXIST_USER"},          status=400 - 존재하지 않는 유저
                {"message": "WRONG_PASSWORD"},          status=400 - 패스워드 불일치
            
            History :
                2021-01-19 - 리펙토링 진행 중 (심원두)
        """
        try:
            payload  = json.loads(request.body)
            
            email    = payload['email'].strip()
            password = payload['password'].strip()
            
            if not CommonUtil.is_blank(email, password):
                raise BlankField
            
            if not CommonUtil.is_email_valid(email):
                raise NotValidEmail
            
            if not User.objects.filter(email=email, is_deleted=0).exists():
                raise NotExistUser
            
            user = User.objects.get(email=email, is_deleted=0)
            
            if not check_password(password, user.password):
                return WrongPassword
            
            access_token = issue_access_token(user.id)
            return JsonResponse(
                {
                    "message": "SIGN_IN_SUCCESS",
                    "access_token" : access_token
                },
                status=200
            )
        
        except KeyError as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except BlankField as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except NotValidEmail as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except NotValidPassword as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except NotExistUser as e:
            return JsonResponse({"message": f"{e}"}, status=400)
        
        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"{e}"}, status=400)


class SocialSignInKaKaoView(View):
    def post(self, request):
        try:
            access_token = request.headers.get("Authorization", None)
            
            if not access_token:
                return JsonResponse({'message': 'TOKEN_REQUIRED'}, status=400)
            
            url = "https://kapi.kakao.com/v2/user/me"
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(url, headers=headers).json()
            
            if not 'email' in response['kakao_account']:
                return JsonResponse({'message': 'EMAIL_REQUIRED'}, status=405)
            
            kakao_user = User.objects.get_or_create(
                name          = response["properties"]["nickname"],
                email         = response["kakao_account"]["email"],
                profile_image = response["properties"]["profile_image"],
            )[0]
            
            token = issue_access_token(kakao_user.id)
            
            return JsonResponse(
                {
                    "token"         : token,
                    "name"          : kakao_user.name,
                    'profile_image' : kakao_user.profile_image
                }, status=200
            )
        
        except json.JSONDecodeError as e:
            return JsonResponse({"message": f"JSON_ERROR:{e}"}, status=400)
        
        except User.DoesNotExist:
            return JsonResponse({"message": "NO_EXIST_USER"}, status=401)
        
        except TypeError:
            return JsonResponse({"message": "TYPE_ERROR"}, status=400)
        
        except KeyError as e:
            return JsonResponse({"message": f"KEY_ERROR:{e}"}, status=400)


class SearchView(View):
    def get(self, request):
        try:
            search = request.GET.get('search')
            sorting = request.GET.get('sorting')
            sub_category_id = request.GET.get('sub_category')
            
            products = Product.objects.select_related(
                'main_category',
                'sub_category',
                'creator'
            ).prefetch_related(
                'kit',
                'detail_category',
                'product_like_user',
                'product_view_user'
            )
            
            filters = {}
            
            if sub_category_id:
                filters['sub_category__name'] = sub_category_id
            
            q = Q()
            
            sortings = {
                None     : '-created_at',
                'updated': '-created_at',
                'views'  : products.annotate(viewcount=Count('product_view_user')).order_by('-viewcount'),
                'popular': products.annotate(count=Count('product_like_user')).order_by('-count')
            }
            if sorting:
                if sorting == 'updated':
                    products = products.order_by(sortings[sorting])
                else:
                    products = sortings[sorting]
            
            if search:
                q &= Q(name__icontains=search) | \
                     Q(main_category__name__icontains=search) | \
                     Q(sub_category__name__icontains=search) | \
                     Q(creator__name__icontains=search) | \
                     Q(kit__name__icontains=search) | \
                     Q(detail_category__name__icontains=search)
            
            if not search:
                return JsonResponse({'message': 'WRONG_KEY'}, status=400)
            
            search_list = [{
                'id'         : product.id,
                'title'      : product.name,
                'thumbnail'  : product.thumbnail_image,
                'subCategory': product.sub_category.name,
                'creator'    : product.creator.name,
                'isLiked'    : True if ProductLike.objects.filter(product_id=product.id).exists() else False,
                'likeCount'  : product.creator.product_like.all().count(),
                'price'      : int(product.price),
                'sale'       : product.sale,
                'finalPrice' : round(int(product.price * (1 - product.sale)), 2)
            } for product in products.filter(q, **filters)]
            
            if not search_list:
                return JsonResponse({'message': 'NO_RESULT'}, status=400)
            return JsonResponse({'search_result': search_list}, status=200)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except TypeError:
            return JsonResponse({'message': 'TYPE_ERROR'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)

class MyPageView(View):
    @login_decorator(login_required=True)
    def get(self, request):
        try:
            user = request.user
            user_object = User.objects.prefetch_related('coupon', 'recently_view__product_like_user',
                                                        'product_like__product_like_user', 'user_product',
                                                        'recently_view__sub_category', 'recently_view__creator',
                                                        'product_like__sub_category', 'product_like__creator').get(
                id=user.id)
            user_profile = {
                'id'          : user_object.id,
                'name'        : user_object.name,
                'profileImage': user_object.profile_image,
                'email'       : user_object.email,
                'point'       : user_object.point,
                'couponNum'   : user_object.coupon.count(),
                'likeNum'     : user_object.product_like.count(),
                'orderNum'    : user_object.user_product.count()
            }
            created_product_list = Product.objects.select_related(
                'creator').filter(creator=user.id)
            #     created_product_list = user_object.filter(creator_id=user.id)
            own_product_list = user_object.user_product.all()
            recently_viewed_list = user_object.recently_view.all()
            like_product_list = user_object.product_like.all()
            created_list = [{
                'classId'   : created.id,
                'title'     : created.name,
                'thumbnail' : created.thumbnail_image,
                'price'     : created.price,
                'sale'      : int(created.sale * 100),
                'finalPrice': round(int(created.price * (1 - created.sale)), 2),
            } for created in created_product_list]
            own_list = [{
                'classId'      : own_product.id,
                'title'        : own_product.name,
                'thumbnail'    : own_product.thumbnail_image,
                'effectiveDate': '평생 수강 쌉가능' if not own_product.effective_time else
                str(((own_product.created_at + own_product.effective_time) -
                     datetime.today() + timedelta(days=1)).days) + '일 남음',
            } for own_product in own_product_list]
            viewed_list = [{
                'classId'    : recent.id,
                'title'      : recent.name,
                'thumbnail'  : recent.thumbnail_image,
                'subCategory': recent.sub_category.name,
                'creator'    : recent.creator.name,
                'isLiked'    : True if recent.filter(product_id=user.recently_view.product.id).exists() else False,
                'likeCount'  : recent.product_like_user.all().count(),
                'price'      : recent.price,
                'sale'       : int((recent.sale) * 100),
                'finalPrice' : round(int(recent.price * (1 - recent.sale)), 2),
            } for recent in recently_viewed_list]
            liked_list = [{
                'classId'    : like_product.id,
                'title'      : like_product.name,
                'thumbnail'  : like_product.thumbnail_image,
                'subCategory': like_product.sub_category.name,
                'creator'    : like_product.creator.name,
                'isLiked'    : True if like_product else False,
                'likeCount'  : like_product.product_like_user.all().count(),
                'price'      : like_product.price,
                'sale'       : int((like_product.sale) * 100),
                'finalPrice' : round(int(like_product.price * (1 - like_product.sale)), 2),
            } for like_product in like_product_list]
            return JsonResponse(
                {'PROFILE': user_profile, 'OWN_PRODUCT': own_list, 'RECENT_VIEW': viewed_list, 'CREATED': created_list,
                 'LIKED'  : liked_list}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'INVALID_USER'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'message': 'INVALID_PRODUCT'}, status=400)
        except RecentlyView.DoesNotExist:
            return JsonResponse({'message': 'INVALID_OBJECT'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)

class CommunityView(View):
    @login_decorator(login_required=True)
    def post(self, request):
        data = json.loads(request.body)
        try:
            user = request.user
            product = Product.objects.get(pk=data['product_id'])
            description = data['description']
            
            Community.objects.create(
                user=user,
                product=product,
                description=description,
            )
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'INVALID_USER'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'message': 'INVALID_PRODUCT'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)
    
    @login_decorator(login_required=True)
    def patch(self, request, id):
        try:
            user_id = request.user.id
            data = json.loads(request.body)
            description = data['description']
            
            community_update = Community.objects.get(pk=id)
            
            if community_update.user.id is not user_id:
                return JsonResponse({'message': 'INVALID_USER'}, status=403)
            community_update.description = description
            community_update.save()
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except Community.DoesNotExist:
            return JsonResponse({'message': 'NO_EXIST_COMMUNITY'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)
    
    @login_decorator(login_required=True)
    def delete(self, request, id):
        try:
            user_id = request.user.id
            community_delete = Community.objects.get(pk=id)
            
            if community_delete.user.id is not user_id:
                return JsonResponse({'message': 'INVALID_USER'}, status=403)
            community_delete.delete()
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except Community.DoesNotExist:
            return JsonResponse({'message': 'NO_EXIST_COMMUNITY'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)
    
    @login_decorator(login_required=True)
    def get(self, request, id):
        try:
            community = Community.objects.select_related('user', 'product', 'product__sub_category',
                                                         'product__creator').prefetch_related(
                'user__community_like', 'user__community_like').get(pk=id)
            comments = community.communitycomment_set.select_related('user').all()
            comment_count = comments.count()
            community_like = community.communitylike_set.all()
            
            community_detail = {
                'id'          : community.id,
                'name'        : community.user.name,
                'profileImage': community.user.profile_image,
                'createdAt'   : community.created_at,
                'content'     : community.description,
                'likeCount'   : community.user.community_like.all().count(),
                'isLiked'     : get_is_like(request.user.id) if request.user else False,
                'commentCount': comment_count,
                'thumbnail'   : community.product.thumbnail_image,
                'subCategory' : community.product.sub_category.name,
                'creator'     : community.product.creator.name,
                'productTitle': community.product.name,
            }
            
            comment_list = [{
                'id'          : comment.id,
                'name'        : comment.user.name,
                'profileImage': comment.user.profile_image,
                'created_at'  : comment.created_at,
                'content'     : comment.content
            } for comment in comments]
            
            return JsonResponse({"community_detail": community_detail, "comment_count": comment_count,
                                 "comment_list"    : comment_list}, status=200)
        except Community.DoesNotExist:
            return JsonResponse({'message': 'NO_EXIST_COMMUNITY'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)

def get_is_like(user_id):
    return CommunityLike.objects.filter(community_id=id, user_id=user_id).exists()

class CommunityCommentView(View):
    @login_decorator(login_required=True)
    def post(self, request):
        data = json.loads(request.body)
        try:
            user = request.user
            content = data['content']
            
            CommunityComment.objects.create(
                user=user,
                communtiy_id=data['community_id'],
                content=content,
            )
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'INVALID_USER'}, status=400)
        except Community.DoesNotExist:
            return JsonResponse({'message': 'INVALID_COMMUNITY'}, status=400)
        except CommunityComment.DoesNotExist:
            return JsonResponse({'message': 'INVALID_COMMENT'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)
    
    @login_decorator(login_required=True)
    def delete(self, request, id):
        user_id = request.user.id
        try:
            community_comment_delete = CommunityComment.objects.get(pk=id)
            if community_comment_delete.user.id is not user_id:
                return JsonResponse({'message': 'INVALID_USER'}, status=403)
            community_comment_delete.delete()
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except CommunityComment.DoesNotExist:
            return JsonResponse({'message': 'NO_EXIST_COMMUNITY'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)

class LectureCommentView(View):
    @login_decorator(login_required=True)
    def post(self, request):
        data = json.loads(request.body)
        try:
            user = request.user
            lecture = Lecture.objects.get(pk=data['lecture_id'])
            content = data['content']
            image_url = data['image_url']
            
            LectureComment.objects.create(
                user=user,
                lecture=lecture,
                content=content,
                image_url=image_url
            )
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message': 'INVALID_USER'}, status=400)
        except Lecture.DoesNotExist:
            return JsonResponse({'message': 'INVALID_LECTURE'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)
    
    @login_decorator(login_required=True)
    def patch(self, request, id):
        data = json.loads(request.body)
        try:
            user_id = request.user.id
            content = data['content']
            lecture_comment_update = LectureComment.objects.get(pk=id)
            
            if lecture_comment_update.user.id != user_id:  # 수정하기 누르자마자 작성자 아니면 걸러지는
                return JsonResponse({'message': 'INVALID_USER'}, status=403)
            lecture_comment_update.content = content
            lecture_comment_update.save()
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except LectureComment.DoesNotExist:
            return JsonResponse({'message': 'NO_EXIST_COMMENT'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)
    
    @login_decorator(login_required=True)
    def delete(self, request, id):
        user_id = request.user.id
        try:
            lecture_comment_delete = LectureComment.objects.get(pk=id)
            if lecture_comment_delete.user.id != user_id:
                return JsonResponse({'message': 'INVALID_USER'}, status=403)
            lecture_comment_delete.delete()
            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except LectureComment.DoesNotExist:
            return JsonResponse({'message': 'NO_EXIST_COMMENT'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)
    
    @login_decorator(login_required=True)
    def get(self, request):
        try:
            user_id = request.user.id
            lecture_comments = LectureComment.objects.select_related('user').filter(user_id=user_id)
            comment_count = LectureComment.objects.all().count()
            comments = [{
                'id'          : lecture_comment.id,
                'name'        : lecture_comment.user.name,
                'profileImage': lecture_comment.user.profile_image,
                'createdAt'   : lecture_comment.created_at,
                'content'     : lecture_comment.content,
            } for lecture_comment in lecture_comments]
            
            return JsonResponse({"comment_count": comment_count, "comment_list": comments}, status=200)
        except LectureComment.DoesNotExist:
            return JsonResponse({'message': 'NO_EXIST_COMMENT'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)


class CommunityLikeView(View):
    @login_decorator(login_required=True)
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = request.user.id
            community_id = data['community_id']
            
            if CommunityLike.objects.prefetch_related('community_like_user').filter(user=user_id,
                                                                                    community=community_id).exists():
                CommunityLike.objects.get(user=user_id, community=community_id).delete()
                return JsonResponse({'message': 'REMOVED'}, status=200)
            
            CommunityLike(
                user_id=user_id,
                community_id=community_id
            ).save()
            return JsonResponse({'message': 'LIKED_COMMUNITY'}, status=201)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)

class ProductLikeView(View):
    @login_decorator(login_required=True)
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = request.user.id
            product_id = data['product_id']
            
            if ProductLike.objects.prefetch_related('product_like_user').filter(user=user_id,
                                                                                product=product_id).exists():
                ProductLike.objects.get(user=user_id, product=product_id).delete()
                return JsonResponse({'message': 'REMOVED'}, status=200)
            
            ProductLike(
                user_id=user_id,
                product_id=data['product_id']
            ).save()
            return JsonResponse({'message': 'LIKED_PRODUCT'}, status=201)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'JSON_DECODE_ERROR:{e}'}, status=400)