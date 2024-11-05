from django.urls import path
from My_App import views

urlpatterns = [
    path('',views.home),
    path('login',views.login),
    path('login_post',views.login_post),

    path('admin_home',views.admin_home),
    path('admin_logout', views.admin_logout),
    path('verify_seller', views.verify_seller),
    path('accept_reject_seller', views.accept_reject_seller),
    path('block_unblock_seller', views.block_unblock_seller),
    path('admin_view_users', views.admin_view_users),
    path('advim_view_complaint', views.advim_view_complaint),
    path('complaint_reply/<id>', views.complaint_reply),
    path('complaint_reply_post', views.complaint_reply_post),
    path('verify_orders', views.verify_orders),
    path('accept_order/<id>', views.accept_order),
    path('reject_order/<id>', views.reject_order),
    path('view_more_order/<id>', views.view_more_order),


    path('seller_registration', views.seller_registration),
    path('seller_home',views.seller_home),
    path('seller_view_profile',views.seller_view_profile),
    path('seller_edit_profile',views.seller_edit_profile),
    path('seller_edit_profile_post',views.seller_edit_profile_post),
    path('seller_manage_products',views.seller_manage_products),
    path('seller_add_product',views.seller_add_product),
    path('edit_product/<id>',views.edit_product),
    path('delete_product/<id>',views.delete_product),
    path('edit_product_post',views.edit_product_post),
    path('seller_view_order_history',views.seller_view_order_history),
    path('seller_logout', views.seller_logout),


    path('user_registration', views.user_registration),
    path('add_new', views.add_new),
    path('user_view_complaint', views.user_view_complaint),
    path('user_home',views.user_home),
    path('view_all_products',views.view_all_products),
    path('search_products',views.search_products),
    path('user_profile',views.user_profile),
    path('edit_profile',views.edit_profile),
    path('edit_profile_post',views.edit_profile_post),
    path('user_logout',views.user_logout),
    path('add_to_cart/<id>',views.add_to_cart),
    path('view_cart',views.view_cart),
    path('remove_from_cart/<id>',views.remove_from_cart),
    path('send_request/<id>',views.send_request),
    path('view_order_status',views.view_order_status),
    path('user_view_more_order_status/<id>',views.user_view_more_order_status),
    path('user_order_history',views.user_order_history),
    # path('send_review/<id>',views.send_review),
    path('on_payment_success',views.on_payment_success),
    path('user_pay_proceed/<id>/<amt>',views.user_pay_proceed),
    path('add_rating',views.add_rating),
    path('verify_seller_product_rate/<sellerid>',views.verify_seller_product_rate),
    path('product_feedback/<pid>',views.product_feedback),
    path('product_feedbackadmin',views.product_feedbackadmin),
    path('view_rec',views.view_rec),
    path('submit_review',views.submit_review,name='submit_review'),



]