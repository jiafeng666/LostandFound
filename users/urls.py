from django.conf.urls import url

from users import views

urlpatterns = [
    url('^register/$', views.RegisterView.as_view(), name='register'),
    url('^login/$', views.LoginView.as_view(), name='login'),
    url('^logout/$', views.LogoutView.as_view()),
    url('^info/$', views.LostView.as_view(), name='info'),
    url('^submit_goods/$', views.SubmitGoodsView.as_view()),
    url('^change_status/$', views.ChangeStatus.as_view()),
    url('^delete_goods/$', views.DeleteGoods.as_view()),
]