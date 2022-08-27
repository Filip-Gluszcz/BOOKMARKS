from actions.utils import create_action
from common.decorators import ajax_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from actions.models import Action

# Create your views here.
@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    followind_ids = request.user.following.values_list('id', flat=True)

    if followind_ids: actions = actions.filter(user_id__in=followind_ids)
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
    
    return render(request, 
                 'account/dashboard.html', 
                 {'section': 'dashboard',
                 'actions': actions})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            
            profile = Profile.objects.create(user=new_user)

            create_action(request.user, 'utworzył konto')

            return render(request, 
                         'registration/register_done.html', 
                         {'new_user': new_user})

    else: user_form = UserRegistrationForm()

    return render(request, 
                 'registration/register.html', 
                 {'user_form': user_form})


@login_required
def edit(request):
    # try:
    #     profile = request.user.profile
    # except Profile.DoesNotExist:
    #     profile = Profile.objects.create(user=request.user)
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, 
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, 
                                       data=request.POST, 
                                       files=request.FILES)
                                       
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, 'Uaktualnienie profilu zakończyło się sukcesem.')
            
        else: messages.error(request, 'Wystąpił błąd podczas uaktualniania profilu.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    
    return render(request, 
                 'account/edit.html', 
                 {'user_form': user_form, 
                  'profile_form': profile_form})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)

    return render(request, 
                 'account/user/list.html', 
                 {'section': 'people', 
                 'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, 
                             username=username, 
                             is_active=True)

    return render(request, 
                 'account/user/detail.html', 
                 {'section': 'people', 
                 'user': user})



@ajax_required
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')

    if action and user_id:
        try:
            user = User.objects.get(id=user_id)

            if user == request.user : return JsonResponse({'status': 'ok'})
            
            if action == 'follow': 
                Contact.objects.create(user_from=request.user, 
                                       user_to=user)

                create_action(request.user, 
                             'obserwuje', 
                             user)

            else: Contact.objects.filter(user_from=request.user, 
                                         user_to=user).delete()
                
            return JsonResponse({'status': 'ok'})
        
        except User.DoesNotExist: return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'status': 'ok'})