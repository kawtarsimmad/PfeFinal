
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import MessageForm
from django.db.models import Q
from users.models import User,Association,Donor

@login_required
def message_list(request):
    association = None
    donor = None
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    if hasattr(request.user, 'dashboard_donor'):
        donor = request.user.dashboard_donor
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            if request.POST.get('send_to_all') == 'true':
                for user in User.objects.exclude(id=request.user.id):
                        new_message = Message(sender=message.sender, recipient=user, content=message.content)
                        new_message.save()
                return redirect('message_list')
            elif request.POST.getlist('selected_users') and request.user.is_admin:
                selected_user_ids = request.POST.getlist('selected_users')
                for user_id in selected_user_ids:
                    recipient = get_object_or_404(User, id=user_id)
                    new_message = Message(sender=message.sender, recipient=recipient, content=message.content)
                    new_message.save()
                return redirect('message_list')
    else:
        form = MessageForm()
    users = User.objects.exclude(id=request.user.id)
    
    return render(request, 'message_list.html', {'users': users, 'association': association, 'donor': donor, 'form': form})

@login_required
def conversation(request, user_id):
    association=None
    donor=None
    recipient = get_object_or_404(User, id=user_id)  
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
        #voir  seulement les conversations avec les admins
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient__dashboard_admin=True)) |
            (Q(recipient=request.user) & Q(sender__dashboard_admin=True))
        ).order_by('timestamp')
        users = User.objects.filter(dashboard_admin=True)

    if hasattr(request.user, 'dashboard_donor'):
        donor = request.user.dashboard_donor
        #voir  seulement les conversations avec les admins
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient__dashboard_admin=True)) |
            (Q(recipient=request.user) & Q(sender__dashboard_admin=True))
        ).order_by('timestamp')
        users = User.objects.filter(dashboard_admin=True)


    if hasattr(request.user, 'dashboard_admin'):
        messages = Message.objects.all()  
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=recipient)) | 
            (Q(sender=recipient) & Q(recipient=request.user))
        ).order_by('timestamp')
        users = users = User.objects.exclude(id=request.user.id)


    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            return redirect('conversation', user_id=recipient.id)
    else:
        form = MessageForm()

   
    return render(request, 'conversation.html', {
        'recipient': recipient,
        'messages': messages,
        'form': form,
        'users': users,
        'association':association,
        'donor':donor,
        
    })

def chat_view(request):
    association=None
    donor=None
    if hasattr(request.user, 'dashboard_association'):
        association = request.user.dashboard_association
    if hasattr(request.user, 'dashboard_donor'):
        donor = request.user.dashboard_donor
    user = request.user
    if user.is_donor or user.is_association:
        admin_user = User.objects.filter(dashboard_admin__isnull=False).first()
        messages = Message.objects.filter(
            (Q(sender=user) & Q(recipient=admin_user)) | (Q(sender=admin_user) & Q(recipient=user))
        ).order_by('timestamp')
        users = [admin_user]

    return render(request, 'chat_page.html', {'users': users, 'messages': messages,'association':association,'donor':donor})

def search_users(request):
    query = request.GET.get('query') 
    user_results = []
    if query:
        user_results = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, 'search_results.html', {'user_results': user_results})

def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.user == message.sender or request.user == message.recipient:
        message.delete()
    
    return redirect('conversation', user_id=message.recipient.id)