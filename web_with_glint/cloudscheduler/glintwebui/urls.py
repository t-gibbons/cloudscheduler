from django.conf.urls import url

from . import views


from .celery_app import image_collection
from .utils import check_collection_task, set_collection_task


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^project_details/(?P<group_name>.+)/$', views.project_details, name='project_details'),
    url(r'^add_repo/(?P<group_name>.+)/$', views.add_repo, name='add_repo'),
    url(r'^manage_repos/(?P<group_name>.+)/$', views.manage_repos, name='manage_repos'),
    url(r'^update_repo/(?P<group_name>.+)/$', views.update_repo, name='update_repo'),
    url(r'^delete_repo/(?P<group_name>.+)/$', views.delete_repo, name='delete_repo'),
    url(r'^save_images/(?P<group_name>.+)/$', views.save_images, name='save_images'),
    url(r'^resolve_conflict/(?P<group_name>.+)/(?P<repo_alias>.+)/$', views.resolve_conflict, name='resolve_conflict'),
    url(r'^manage_users/$', views.manage_users, name='manage_users'),
    url(r'^user_settings/$', views.user_settings, name='user_settings'),
    url(r'^update_user/$', views.update_user, name='update_user'),
    url(r'^self_update_user/$', views.self_update_user, name='self_update_user'),
    url(r'^add_user/$', views.add_user, name='add_user'),
    url(r'^delete_user/$', views.delete_user, name='delete_user'),
    url(r'^manage_accounts/$', views.manage_accounts, name='manage_accounts'), 
    url(r'^delete_account/$', views.delete_account, name='delete_account'), 
    url(r'^add_account/$', views.add_account, name='add_account'), 
    url(r'^update_account/$', views.update_account, name='update_account'), 
    url(r'^delete_user_account/$', views.delete_user_account, name='delete_user_account'),
    url(r'^add_user_account/$', views.add_user_account, name='add_user_account'),
    url(r'^download_image/(?P<account_name>.+)/(?P<image_name>.+)/$', views.download_image, name='download_image'),
    url(r'^upload_image/(?P<account_name>.+)/$', views.upload_image, name='upload_image'),
    url(r'^save_hidden_images/(?P<account_name>.+)/$', views.save_hidden_images, name='save_hidden_images'),
]

# Check if the image collection task is running, if not start it and set it to running
collection_started = check_collection_task()
if not collection_started:
    image_collection.apply_async(queue='image_collection')
    set_collection_task(True)

