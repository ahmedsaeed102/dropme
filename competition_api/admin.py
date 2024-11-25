from django.contrib import admin
from .models import Competition, CompetitionRanking, Resource

class CompetitionRankingAdmin(admin.ModelAdmin):
    list_display = ["user", "competition", "points"]
    list_filter = ["competition"]

admin.site.register(Competition)
admin.site.register(CompetitionRanking, CompetitionRankingAdmin)
admin.site.register(Resource)
