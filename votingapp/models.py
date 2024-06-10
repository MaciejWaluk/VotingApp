"""
This file defines the models for the voting application.
"""

from django.contrib.auth.models import User, Group
from django.db import models


class VotingUser(models.Model):
    """
    Represents a voter registered in the voting system. Extends the default User model with additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=100, unique=True)  # Ensures unique email addresses
    nr_pesel = models.CharField(max_length=11)

    def __str__(self):
        return self.user.username


class Election(models.Model):
    """
    Represents an election with details and configuration.
    """
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(VotingUser, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=100)
    max_votes = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    allowed_groups = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return self.type


class Constraint(models.Model):
    """
    Represents a constraint associated with an election, possibly a question that voters must answer.
    """
    id = models.AutoField(primary_key=True)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)
    question = models.CharField(max_length=100)

    def __str__(self):
        return f"Constraint for election {self.election.type}"  # Optional for better representation


class Voted_User(models.Model):
    """
    Represents a relationship between a VotingUser and an Election, indicating that the user has voted in that election.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(VotingUser, on_delete=models.DO_NOTHING)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.user} voted in {self.election}"  # Optional for better representation


class Candidate(models.Model):
    """
    Represents a candidate in an election with name, surname, and description.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} {self.surname}"


class Election_Candidate(models.Model):
    """
    Represents a relationship between an Election and a Candidate, indicating that the candidate participates in the election.
    """
    id = models.AutoField(primary_key=True)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.candidate} is a candidate in {self.election}"  # Optional for better representation


class Vote(models.Model):
    """
    Represents a vote cast by a user for a candidate in a specific election.
    """
    id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)
    date = models.DateField()
