from django.urls import path
from .views import show_dish, show_order, get_order, dish_comments, add_comment, toggle_preference, show_preferences


app_name = 'dish'
urlpatterns = [
    path('dish/', show_dish, name='show_dish'),
    path('order/', show_order, name='show_order'),
    path('get_order/<slug:dish_id>', get_order, name='get_order'),
    path('dish/<int:dish_id>/comments/', dish_comments, name='dish_comments'),
    path('dish/<int:dish_id>/add_comment/', add_comment, name='add_comment'),
    path('dish/dish/<int:dish_id>/toggle_preference/<str:preference_type>/', toggle_preference, name='toggle_preference'),
    path('preferences/<str:preference_type>/', show_preferences, name='show_preferences'),
]