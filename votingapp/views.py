from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django import forms
from .models import VotingUser
from django.contrib.auth.models import User
from .models import Voted_User


from votingapp.models import Election, Election_Candidate, Candidate, Vote


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
        return voting_user


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('election_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to home page after registration
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def election_list(request):
    today = date.today()
    user = request.user
    try:
        voting_user = user.votinguser
    except VotingUser.DoesNotExist:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    all_elections = Election.objects.all()
    voted_elections = Voted_User.objects.filter(user=voting_user).values_list('election_id', flat=True)
    remaining_elections = all_elections.exclude(id__in=voted_elections)

    return render(request, 'election_list.html', {'elections': remaining_elections, 'today': today})


def election_detail(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = Candidate.objects.filter(election_candidate__election=election)
    user = request.user  # Get the current user

    # Get the VotingUser object associated with the logged-in user
    try:
        voting_user = user.votinguser
    except VotingUser.DoesNotExist:
        # Handle the case where the VotingUser object does not exist
        # This might happen if the user is not properly associated with a VotingUser
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')  # Redirect to the home page or another appropriate view

    # Check if the user has already voted in the election
    if Voted_User.objects.filter(user=voting_user, election=election).exists():
        messages.error(request, 'You have already voted in this election.')
        return redirect('election_list')  # Redirect to the elections list view

    if request.method == 'POST':
        selected_candidates = request.POST.getlist('candidate')
        max_votes = election.max_votes

        if len(selected_candidates) != max_votes:
            messages.error(request, f'Please select exactly {max_votes} candidates.')
        else:
            # Create Vote objects for selected candidates
            for candidate_id in selected_candidates:
                candidate = get_object_or_404(Candidate, pk=candidate_id)
                Vote.objects.create(candidate=candidate, election=election, date=timezone.now())  # Set the date
            # Register the user as voted in the election
            Voted_User.objects.create(user=voting_user, election=election)

            messages.success(request, 'Your vote has been submitted successfully.')
            return redirect('election_list')  # Redirect to the elections list view

    return render(request, 'election_detail.html', {'election': election, 'candidates': candidates})

