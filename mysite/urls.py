from django.conf.urls import url
from mysite import views

urlpatterns = [
    url('^$', views.IndexView.as_view(), name='index'),
    url(r'^email/active/$', views.SentEmailVial.as_view()),
    url(r'^email/verification/$', views.VerificationEmail.as_view())
]