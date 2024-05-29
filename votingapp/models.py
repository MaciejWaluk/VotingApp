from django.contrib.auth.models import User, Group
from django.db import models


class VotingUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    nr_pesel = models.CharField(max_length=11)


class Election(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(VotingUser, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=100)
    max_votes = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    allowed_groups = models.ManyToManyField(Group, blank=True)


class Constraint(models.Model):
    id = models.AutoField(primary_key=True)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)
    question = models.CharField(max_length=100)


class Voted_User(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(VotingUser, on_delete=models.DO_NOTHING)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)


class Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def get_name(self):
        return self.name


class Election_Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING)


class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING)
    election = models.ForeignKey(Election, on_delete=models.DO_NOTHING)
    date = models.DateField()
