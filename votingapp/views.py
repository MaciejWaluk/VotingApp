from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from votingapp.models import Election, Election_Candidate, Candidate, Vote


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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home page after registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def election_list(request):
    elections = Election.objects.all()
    return render(request, 'election_list.html', {'elections': elections})


def election_detail(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = Candidate.objects.filter(election_candidate__election=election)

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
            messages.success(request, 'Your vote has been submitted successfully.')
            return redirect('election_list')  # Redirect to the elections list view

    return render(request, 'election_detail.html', {'election': election, 'candidates': candidates})
