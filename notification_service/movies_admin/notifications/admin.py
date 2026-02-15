from django.contrib import admin
from django.contrib import messages
from movies.models import FilmWork
from .services import send_notification


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "rating")
    search_fields = ("title",)
    actions = ["send_new_release_notification"]

    @admin.action(description="Send notification about selected movies")
    def send_new_release_notification(self, request, queryset):
        count = 0

        for film in queryset:
            payload = {
                "title": film.title,
                "description": film.description,
                "rating": film.rating,
                "type": film.type,
            }

            send_notification(
                event_key="movie.new_release",
                target_segment="subscribed_users",
                payload=payload,
            )

            count += 1

        self.message_user(
            request,
            f"Sent notifications for {count} movies",
            level=messages.SUCCESS,
        )
