from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('royalties/', views.royalty_list, name='royalty_list'),
    path('subscriptions/plans/', views.subscription_plans, name='subscription_plans'),
    path('subscriptions/subscribe/', views.subscribe, name='subscribe'),
    path('subscriptions/current/', views.current_subscription, name='current_subscription'),
]
