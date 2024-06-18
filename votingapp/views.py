"""
This file defines the view functions for the voting application.

The views handle user authentication (login, logout, registration),
election list display (ongoing and ended elections based on user groups),
voting process (candidate selection and vote casting), and ended election report generation (HTML and PDF).

Logging is set up to track user actions and potential issues.
"""

import logging

from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa

from votingapp.models import Election, Candidate, Vote
from .models import Voted_User, VotingUser

# Set up logging
logger = logging.getLogger(__name__)


class RegistrationForm(forms.ModelForm):
    """
    Custom form for user registration, adding password confirmation and logic to associate the VotingUser with the created User instance.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = VotingUser
        fields = ['email', 'nr_pesel']  # Add additional fields here

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            logger.debug("Password mismatch in registration form.")
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        voting_user = super().save(commit=False)
        username = self.cleaned_data['email']
        user = User.objects.create_user(username=username, email=username, password=self.cleaned_data['password1'])
        voting_user.user = user
        if commit:
            voting_user.save()
        logger.info(f"New user registered: {username}")
        return voting_user


def login_view(request):
    """
    Handles login functionality: processes login form submission, authenticates users, and redirects to the election list on success.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    HttpResponse:
        - Renders the login page with an authentication form if the request method is GET.
        - Redirects to the election list page on successful login.
        - Re-renders the login page with error messages if authentication fails.

    Template:
    login.html: Displays the login form.

    Context:
    form (AuthenticationForm): The authentication form instance.
    """

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User logged in: {user.username}")
            return redirect('election_list')
        else:
            logger.warning("Login failed with provided credentials.")
            logger.debug(f"Login attempt failed with data: {request.POST}")
    else:
        form = AuthenticationForm()
        logger.debug("Rendering login form.")
    return render(request, 'login.html', {'form': form})


def register_view(request):
    """
    Handles user registration: processes registration form submission, saves user data, and redirects to login on success.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    HttpResponse:
        - Renders the registration page with a registration form if the request method is GET.
        - Redirects to the login page on successful registration.
        - Re-renders the registration page with error messages if form validation fails.

    Template:
    register.html: Displays the registration form.

    Context:
    form (RegistrationForm): The custom registration form instance.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info("User registration successful.")
            return redirect('login')
        else:
            logger.warning("User registration failed.")
            logger.debug(f"Registration form data: {request.POST}")
    else:
        form = RegistrationForm()
        logger.debug("Rendering registration form.")
    return render(request, 'register.html', {'form': form})


@login_required
def logout_view(request):
    """
    Logs out the current user and redirects to the login page.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    HttpResponse: Redirects to the login page.
    """

    user = request.user
    logout(request)
    logger.info(f"User logged out: {user.username}")
    return redirect('login')


@login_required
def election_list(request):
    """
    Displays a list of ongoing and ended elections for the logged-in user, considering their authorized groups and voting history.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    HttpResponse: Renders the election list page with ongoing and ended elections.

    Template:
    election_list.html: Displays the list of ongoing and ended elections.

    Context:
    ongoing_elections (QuerySet): The list of ongoing elections the user is authorized to vote in.
    ended_elections (QuerySet): The list of ended elections the user was authorized to vote in.
    """
    user = request.user
    try:
        voting_user = user.votinguser
    except VotingUser.DoesNotExist:
        messages.error(request, 'You are not authorized to access this page.')
        logger.warning(f"Unauthorized access attempt by user: {user.username}")
        return redirect('login')

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
    """
    Generates a PDF file with a report about a given election.

    Parameters:
    template_path (str): The path to the HTML template.
    context (dict): The context to be put in the document.

    Returns:
    HttpResponse:
        - The PDF file as a downloadable response.
        - An error message if PDF generation fails.
    """
    template = get_template(template_path)
    html = template.render(context).encode('utf-8')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="election_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf-8')
    if pisa_status.err:
        logger.error("Error generating PDF.")
        return HttpResponse('We had some errors <pre>' + str(pisa_status.err) + '</pre>', status=500)
    logger.debug("PDF generated successfully.")
    return response


def ended_elections_report(request, election_id):
    """
    Generates a report of an ended election with info such as the number of total votes and the number of votes for each candidate in the election.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.
    election_id (int): The primary key of the election for which the report is generated.

    Returns:
    HttpResponse:
        - Renders the ended elections report page if 'pdf' is not in GET parameters.
        - Returns the PDF report if 'pdf' is in GET parameters.

    Template:
    ended_elections_report.html: Displays the ended elections report.

    Context:
    election (Election): The election instance being reported.
    total_votes (int): The total number of votes in the election.
    candidate_votes (dict): A dictionary mapping candidate names to their vote counts.
    date (str): The current date formatted as 'YYYY-MM-DD'.
    """

    election = get_object_or_404(Election, pk=election_id)
    votes = Vote.objects.filter(election=election)
    total_votes = votes.count()
    candidate_votes = {}
    for vote in votes:
        candidate_full_name = f"{vote.candidate.name} {vote.candidate.surname}"
        if candidate_full_name in candidate_votes:
            candidate_votes[candidate_full_name] += 1
        else:
            candidate_votes[candidate_full_name] = 1

    eligible_voters_count = User.objects.filter(groups__in=election.allowed_groups.all()).distinct().count()
    voted_users_count = Voted_User.objects.filter(election=election).count()

    if eligible_voters_count == 0:
        voting_percentage = 0
    else:
        voting_percentage = (voted_users_count / eligible_voters_count) * 100

    context = {
        'election': election,
        'total_votes': total_votes,
        'candidate_votes': candidate_votes,
        'voting_percentage': voting_percentage,
        'date': timezone.now().strftime('%Y-%m-%d')
    }

    if 'pdf' in request.GET:
        logger.debug(f"Generating PDF report for election ID: {election_id}")
        return generate_pdf('election_report_template.html', context)

    logger.info(f"Ended elections report accessed for election ID: {election_id}")
    return render(request, 'ended_elections_report.html', context)


def election_detail(request, election_id):
    """
    Handles the display and submission of election details and voting process.

    This view function manages the following tasks:
    1. Retrieves the election and associated candidates based on the provided election ID.
    2. Checks if the user is authorized to vote and if they have already voted in the election.
    3. Processes the voting form submission by validating the selected candidates and recording the votes.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.
    election_id (int): The primary key of the election to be displayed.

    Returns:
    HttpResponse:
        - Renders the election detail page if the request method is GET.
        - Redirects to the election list page with a success message after successful voting.
        - Redirects to the login page if the user is not authorized.
        - Redirects to the election list page if the user has already voted.

    Raises:
    Http404: If the election or candidate does not exist.

    Template:
    election_detail.html: Displays the details of the election and the list of candidates.

    Context:
    election (Election): The election instance being displayed.
    candidates (QuerySet): The list of candidates associated with the election.

    Examples:
    - A user accesses the election detail page: GET request to '/election/<election_id>/'
    - A user submits their vote: POST request to '/election/<election_id>/'

    """

    election = get_object_or_404(Election, pk=election_id)
    candidates = Candidate.objects.filter(election_candidate__election=election)
    user = request.user

    try:
        voting_user = user.votinguser
    except VotingUser.DoesNotExist:
        messages.error(request, 'You are not authorized to access this page.')
        logger.warning(f"Unauthorized access attempt by user: {user.username}")
        return redirect('login')

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
            logger.info(f"User {user.username} successfully voted in election ID: {election_id}")
            return redirect('election_list')

    logger.debug(f"Rendering election detail page for election ID: {election_id}")
    return render(request, 'election_detail.html', {'election': election, 'candidates': candidates})
