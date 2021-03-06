from django.contrib import admin
from .models import Subscriber, Newsletter


def send_newsletter(modeladmin, request, queryset):
    for newsletter in queryset:
        newsletter.send(request)


send_newsletter.short_description = "Send selected newsletters to subscribers"


class NewsletterAdmin(admin.ModelAdmin):
    actions = [send_newsletter]


admin.site.register(Subscriber)
admin.site.register(Newsletter, NewsletterAdmin)
