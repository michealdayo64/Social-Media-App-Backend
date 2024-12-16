from account.views import get_tokens_for_user


def get_user_token(request):
    user = request.user
    return {'user_access_token': get_tokens_for_user(user)['token']['access']}