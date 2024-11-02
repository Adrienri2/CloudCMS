from django.urls import path
from . import views
from accounts.views import UserListView, EditUserView
from .views import blog_versions, blog_version_preview, GetBlogStatusView, BlogPreviewView, schedule_publication, RevertToVersionView, SetFeaturedBlogView, BlogDetailView, DeleteBlog

app_name = "manage"

urlpatterns = [
    path("blog/", views.ManageBlog.as_view(), name="blog"),
    path("category/", views.ManageCategory.as_view(), name="category"),
    path("comment/", views.ManageComment.as_view(), name="comment"),

    path('kanban/', views.KanbanView.as_view(), name='kanban'),
    path('change_blog_status/<int:blog_id>/', views.ChangeBlogStatusView.as_view(), name='change_blog_status'),
    path('blog_versions/<int:blog_id>/', blog_versions, name='blog_versions'),
    path('blog_version_preview/<int:version_id>/', blog_version_preview, name='blog_version_preview'),
    path('get_blog_status/<int:blog_id>/', GetBlogStatusView.as_view(), name='get_blog_status'),
    path('blog_preview/<int:blog_id>/', BlogPreviewView.as_view(), name='blog_preview'),
    path('revert_to_version/', RevertToVersionView.as_view(), name='revert_to_version'),




    path("create/blog/", views.CreateBlog.as_view(), name="create_blog"),
    path("create/category/", views.CreateCategory.as_view(), name="create_category"),

    path("delete/blog/<int:id>/", DeleteBlog.as_view(), name="delete_blog"),
    path("delete/category/<int:id>", views.DeleteCategory.as_view(), name="delete_category"),
    path("delete/comment/<int:id>", views.DeleteComment.as_view(), name="delete_comment"),

    path("edit/blog/<int:id>/", views.EditBlog.as_view(), name="edit_blog"),
    path("edit/category/<int:id>", views.EditCategory.as_view(), name="edit_category"),
    path('users/', UserListView.as_view(), name='users'),
    path('edit/<int:user_id>/', EditUserView.as_view(), name='edit_user'),
    path('schedule_publication/<int:blog_id>/', schedule_publication, name='schedule_publication'),
    path('set_featured_blog/<int:blog_id>/', SetFeaturedBlogView.as_view(), name='set_featured_blog'),
    path('blogs/<int:id>/', BlogDetailView.as_view(), name='blog_detail'),



    
]
