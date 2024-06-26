# Generated by Django 5.0.3 on 2024-06-17 15:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=100)),
                ('max_votes', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('allowed_groups', models.ManyToManyField(blank=True, to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='Election_Candidate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='votingapp.candidate')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='votingapp.election')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='votingapp.candidate')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='votingapp.election')),
            ],
        ),
        migrations.CreateModel(
            name='VotingUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=100, unique=True)),
                ('nr_pesel', models.CharField(max_length=11)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Voted_User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='votingapp.election')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='votingapp.votinguser')),
            ],
        ),
        migrations.AddField(
            model_name='election',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='votingapp.votinguser'),
        ),
    ]
