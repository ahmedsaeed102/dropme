from django.contrib import admin
from .models import Competition, CompetitionRanking, Resource

admin.site.register(Competition)
admin.site.register(CompetitionRanking)
admin.site.register(Resource)
