from django.contrib import admin

from .models import (VotingUser, Election, Constraint, Voted_User, Candidate, Election_Candidate, Vote)


class CandidateAdmin(admin.ModelAdmin):
    search_fields = ["name", "surname"]
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'surname')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    list_display = ["name", "surname", "description"]


class VotingUserAdmin(admin.ModelAdmin):
    search_fields = ["email", "nr_pesel"]
    list_display = ["email", "nr_pesel"]


class ElectionCandidatesAdmin(admin.ModelAdmin):
    list_display = ["election_name", "candidate_name", "candidate_surname"]

    def election_name(self, obj):
        return obj.election.type

    def candidate_name(self, obj):
        return obj.candidate.name

    def candidate_surname(self, obj):
        return obj.candidate.surname

class VotedUserAdmin(admin.ModelAdmin):
    list_display = ["user_name", "election_name"]

    def election_name(self, obj):
        return obj.election.type

    def user_name(self, obj):
        return obj.user.email

class ElectionsAdmin(admin.ModelAdmin):
    search_fields = ["type"]
    fieldsets = (
        (None, {
            'fields': ('creator',)
        }),
        ('Date', {
            'fields': ('start_date', 'end_date')
        }),
        ('Details', {
            'fields': ('type', 'max_votes')
        }),
        ('Groups', {
            'fields': ('allowed_groups',)
        }),
    )
    list_display = ["type", "start_date", "end_date"]


class VoteAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Vote information', {
            'fields': ('candidate', 'election')
        }),
        ('Details', {
            'fields': ('date',)
        }),
    )
    list_display = ["candidate_name", "candidate_surname", "election_name", "date"]

    def election_name(self, obj):
        return obj.election.type

    def candidate_name(self, obj):
        return obj.candidate.name

    def candidate_surname(self, obj):
        return obj.candidate.surname

admin.site.register(VotingUser, VotingUserAdmin)
admin.site.register(Election, ElectionsAdmin)
admin.site.register(Constraint)
admin.site.register(Voted_User, VotedUserAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Election_Candidate, ElectionCandidatesAdmin)
admin.site.register(Vote, VoteAdmin)
