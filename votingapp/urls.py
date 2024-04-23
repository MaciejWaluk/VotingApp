from django.urls import path
from .views import login_view, register_view, election_list, election_detail

urlpatterns = [
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('elections/', election_list, name='election_list'),
    path('elections/<int:election_id>/', election_detail, name='election_detail'),

]