from django.contrib.auth.views import LoginView
from django.urls import reverse

class login(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Ini akan selalu mengarahkan ke kitchen-display setelah login
        return reverse('kitchen_display:kitchen-display')
    