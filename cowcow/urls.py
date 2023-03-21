from django.urls import path
from .views import MyListView, ListSizeView

urlpatterns = [
    path('cowcow/<str:address>/', MyListView.as_view(), name='my-list'),
    path('cowcow/<str:address>/size/', ListSizeView.as_view(), name='list-size'),
]
