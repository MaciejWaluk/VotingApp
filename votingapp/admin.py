from django.contrib import admin

from .models import (VotingUser, Election, Constraint, Voted_User, Candidate, Election_Candidate, Vote)

admin.site.register(VotingUser)
admin.site.register(Election)
admin.site.register(Constraint)
admin.site.register(Voted_User)
admin.site.register(Candidate)
admin.site.register(Election_Candidate)
admin.site.register(Vote)


