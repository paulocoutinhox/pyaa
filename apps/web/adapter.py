from allauth.account.adapter import DefaultAccountAdapter


class AppAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True

    def new_user(self, request):
        user = super(AppAccountAdapter, self).new_user(request)
        return user
