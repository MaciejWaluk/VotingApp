"""
This file registers the models defined in the `votingapp` app with the Django admin interface.

It creates custom admin classes for each model, specifying:
    - Search fields for easy filtering
    - Fieldsets for grouping related fields in the admin interface
    - List displays to define the columns shown in the admin list view
    - Custom methods to display related model data in a clear way (e.g., election_name, candidate_name)
"""

from django.contrib import admin

from .models import (VotingUser, Election, Constraint, Voted_User, Candidate, Election_Candidate, Vote)


class CandidateAdmin(admin.ModelAdmin):
    """
    Admin class for the Candidate model.
    """
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
    """
    Admin class for the VotingUser model.
    """
    search_fields = ["email", "nr_pesel"]
    list_display = ["email", "nr_pesel"]


class ElectionCandidatesAdmin(admin.ModelAdmin):
    """
    Admin class for the Election_Candidate model (relationship between Elections and Candidates).
    """
    list_display = ["election_name", "candidate_name", "candidate_surname"]

    def election_name(self, obj):
        """
        Custom method to display the election type for Election_Candidate objects.
        """
        return obj.election.type

    def candidate_name(self, obj):
        """
        Custom method to display the candidate's name for Election_Candidate objects.
        """
        return obj.candidate.name

    def candidate_surname(self, obj):
        """
        Custom method to display the candidate's surname for Election_Candidate objects.
        """
        return obj.candidate.surname


class VotedUserAdmin(admin.ModelAdmin):
    """
    Admin class for the Voted_User model.
    """
    list_display = ["user_name", "election_name"]

    def election_name(self, obj):
        """
        Custom method to display the election type for Voted_User objects.
        """
        return obj.election.type

    def user_name(self, obj):
        """
        Custom method to display the user's email for Voted_User objects.
        """
        return obj.user.email


class ElectionsAdmin(admin.ModelAdmin):
    """
    Admin class for the Election model.
    """
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
    """
    Admin class for the Vote model.
    """
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
        """
        Custom method to display the election type for Vote objects.
        """
        return obj.election.type

    def candidate_name(self, obj):
        """
        Custom method to display the candidate's name for Vote objects.
        """
        return obj.candidate.name

    def candidate_surname(self, obj):
        """
        Custom method to display the candidate's surname for Vote objects.
        """
        return obj.candidate.surname


admin.site.register(VotingUser, VotingUserAdmin)
admin.site.register(Election, ElectionsAdmin)
admin.site.register(Constraint)
admin.site.register(Voted_User, VotedUserAdmin)
admin.site.register(Candidate, CandidateAdmin)
