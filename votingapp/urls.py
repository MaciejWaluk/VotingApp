from django.urls import path
from .views import login_view, register_view, election_list, election_detail, logout_view, ended_elections_report

urlpatterns = [
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('elections/', election_list, name='election_list'),
    path('elections/<int:election_id>/', election_detail, name='election_detail'),
    path('logout/', logout_view, name='logout'),
    path('elections/<int:election_id>/report/', ended_elections_report, name='ended_elections_report'),

]