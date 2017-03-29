from django.conf.urls import url

from . import views

# app_name = 'products' --------- should name space everything later, it looks much better
# TODO this^^^^
urlpatterns = [
    url(r'^add/', views.add_product, name='add_product'),
    url(r'^list/', views.list_product, name='list_product'),
    url(r'^update/(?P<product_id>[\w-]+)/', views.update_product, name='update_product'),
    url(r'^delete/(?P<product_id>[\w-]+)/', views.delete_product, name='delete_product'),
    url(r'^view/(?P<product_id>[\w-]+)/', views.view_product, name='view_product'),
    url(r'^image_upload/(?P<product_id>[\w-]+)/', views.image_upload, name='image_upload'),
    url(r'^image/delete/(?P<image_id>[\w-]+)/', views.image_delete, name='image_delete'),
    url(r'^feedback/(?P<product_id>[\w-]+)', views.get_product_feedback, name='product_feedback'),
    # optional URL FIRST
    url(r'^category/(?P<category_slug>[\w-]+)/(?P<subcategory_slug>[\w-]+)/', views.child_categories,
        name='view_child_categories'),
    url(r'^category/(?P<category_slug>[\w-]+)/', views.parent_categories, name='view_parent_categories'),
]
