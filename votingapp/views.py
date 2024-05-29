import logging
from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from django import forms
from xhtml2pdf import pisa

from .models import VotingUser
from django.contrib.auth.models import User
from .models import Voted_User
from django.http import HttpResponse

from votingapp.models import Election, Election_Candidate, Candidate, Vote

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = VotingUser
        fields = ['email', 'nr_pesel']  # Add additional fields here

    def clean_password2(self):
        # Check if the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        voting_user = super().save(commit=False)
        username = self.cleaned_data['email']  # Use email as username
        user = User.objects.create_user(username=username, email=username, password=self.cleaned_data['password1'])
        voting_user.user = user  # Associate the VotingUser with the User instance
        if commit:
            voting_user.save()
        logger.info(f"New user registered: {username}")
        return voting_user


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User logged in: {user.username}")
            return redirect('election_list')
        else:
            logger.warning("Login failed with provided credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info("User registration successful.")
            return redirect('login')  # Redirect to home page after registration
        else:
            logger.warning("User registration failed.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def logout_view(request):
    user = request.user
    logout(request)
    logger.info(f"User logged out: {user.username}")
    return redirect('login')


@login_required
def election_list(request):
    user = request.user
    try:
        voting_user = user.votinguser
    except VotingUser.DoesNotExist:
        messages.error(request, 'You are not authorized to access this page.')
        logger.warning(f"Unauthorized access attempt by user: {user.username}")
        return redirect('home')

    user_groups = voting_user.user.groups.all()
    voted_elections = Voted_User.objects.filter(user=voting_user).values_list('election_id', flat=True)
    current_date = timezone.now().date()
    ongoing_elections = Election.objects.filter(end_date__gte=current_date, allowed_groups__in=user_groups)
    ongoing_elections = ongoing_elections.exclude(id__in=voted_elections)
    ended_elections = Election.objects.filter(end_date__lt=current_date, allowed_groups__in=user_groups)

    logger.info(f"Election list accessed by user: {user.username}")

    return render(request, 'election_list.html',
                  {'ongoing_elections': ongoing_elections, 'ended_elections': ended_elections})


def generate_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="election_report.pdf"'
    pisa_status = pisa.CreatePDF(
        html, dest=response
    )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def ended_elections_report(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    votes = Vote.objects.filter(election=election)
    total_votes = votes.count()
    candidate_votes = {}
    for vote in votes:
        candidate_name = vote.candidate.name
        if candidate_name in candidate_votes:
            candidate_votes[candidate_name] += 1
        else:
            candidate_votes[candidate_name] = 1

    context = {
        'election': election,
        'total_votes': total_votes,
        'candidate_votes': candidate_votes
    }

    if 'pdf' in request.GET:
        return generate_pdf('ended_elections_report.html', context)

    logger.info(f"Ended elections report accessed for election ID: {election_id}")
    return render(request, 'ended_elections_report.html', context)



def election_detail(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = Candidate.objects.filter(election_candidate__election=election)
    user = request.user

    try:
        voting_user = user.votinguser
    except VotingUser.DoesNotExist:
        messages.error(request, 'You are not authorized to access this page.')
        logger.warning(f"Unauthorized access attempt by user: {user.username}")
        return redirect('home')

    if Voted_User.objects.filter(user=voting_user, election=election).exists():
        messages.error(request, 'You have already voted in this election.')
        logger.info(f"User {user.username} attempted to vote again in election ID: {election_id}")
        return redirect('election_list')

    if request.method == 'POST':
        selected_candidates = request.POST.getlist('candidate')
        max_votes = election.max_votes

        if len(selected_candidates) > max_votes:
            messages.error(request, f'Please select maximally {max_votes} candidates.')
            logger.warning(f"User {user.username} selected too many candidates in election ID: {election_id}")
        else:
            for candidate_id in selected_candidates:
                candidate = get_object_or_404(Candidate, pk=candidate_id)
                Vote.objects.create(candidate=candidate, election=election, date=timezone.now())  # Set the date

            Voted_User.objects.create(user=voting_user, election=election)
            messages.success(request, 'Your vote has been submitted successfully.')
            return redirect('election_list')

    return render(request, 'election_detail.html', {'election': election, 'candidates': candidates})
