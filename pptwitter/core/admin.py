from flask_peewee.admin import Admin, AdminPanel, ModelAdmin

from . import app, celery
from .auth import auth
from .model import Config, Tweet, User


class TasksPanel(AdminPanel):

    template_name = "admin/tasks.html"

    def get_urls(self):
        return ()

    def get_context(self):
        ins = celery.control.inspect()
        return {
            "scheduled_tasks": ins.scheduled(),
            "active_tasks": ins.active()
        }


class ConfigAdmin(ModelAdmin):

    columns = ("name", "value")


class TweetAdmin(ModelAdmin):

    columns = ("id", "created_at", "tweeted_by", "text", "score")


class UserAdmin(ModelAdmin):

    columns = ("username", "email", "admin")


admin = Admin(app, auth, branding="Power Poetry Twitter Demo")
admin.register(Config, ConfigAdmin)
admin.register(Tweet, TweetAdmin)
admin.register(User, UserAdmin)
admin.register_panel("Celery Tasks", TasksPanel)

admin.setup()
