from allauth.account.adapter import DefaultAccountAdapter


class AppAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        return True
