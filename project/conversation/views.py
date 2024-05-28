
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message,Conversation
from .models import User

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.http import HttpResponseForbidden

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user)
    return render(request, 'inbox.html', {'messages': messages})

@login_required
def send_message(request):
    if not request.user.is_admin:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à créer des messages.")

    users = User.objects.exclude(is_admin=True).exclude(is_superuser=True)

    if request.method == 'POST':
        sender = request.user
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        recipient_username = request.POST.get('recipient_username')
        recipients = None

        if recipient_username == 'all':
            recipients = users
        elif recipient_username:
            recipient = User.objects.filter(username=recipient_username).first()
            if recipient:
                recipients = [recipient]

        if recipients:
            for recipient in recipients:
                # Vérifier s'il existe une conversation entre l'expéditeur et le destinataire sans tenir compte de l'ordre
                conversation = Conversation.objects.filter(
                    participants=sender
                ).filter(participants=recipient).first()

                # Si aucune conversation n'existe, en créer une nouvelle
                if not conversation:
                    conversation = Conversation.objects.create(
                        subject=f"Conversation entre {sender.username} et {recipient.username}"
                    )
                    conversation.participants.add(sender, recipient)

                # Créer un message pour chaque destinataire
                Message.objects.create(
                    conversation=conversation,
                    sender=sender,
                    recipient=recipient,
                    subject=subject,
                    body=body
                )
            return redirect('chat_page')
        else:
            return render(request, {'message': 'Destinataire non trouvé.'})
    else:
        return render(request, 'send_message.html', {'users': users})

@login_required
def reply_message(request, message_id):
    original_message = get_object_or_404(Message, pk=message_id)
    if request.method == 'POST':
        sender = request.user
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        recipient = original_message.sender
        conversation = original_message.conversation

        # Create message
        Message.objects.create(sender=sender, recipient=recipient, subject=subject, body=body, conversation=conversation, reply_to=original_message)
        return redirect('chat_page')
    else:
        return render(request, 'reply_message.html', {'original_message': original_message})


@login_required
def messages(request):
    received_messages = Message.objects.filter(recipient=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    return render(request, 'messages.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    })


def chat_page(request):
    user = request.user
    conversations = Conversation.objects.filter(messages__sender=user) | Conversation.objects.filter(messages__recipient=user)
    users = User.objects.exclude(is_admin=True).exclude(is_superuser=True)

    # Supprimer les doublons (si une conversation a des messages envoyés et reçus par le même utilisateur)
    conversations = conversations.distinct()    
    return render(request, 'chat_page.html', {'conversations': conversations,'users':users})



@login_required
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Vérifier si l'utilisateur fait partie des participants de la conversation
    if request.user not in conversation.participants.all():
        return HttpResponseForbidden("You are not allowed to delete this conversation.")

    # Supprimer tous les messages associés
    conversation.messages.all().delete()
    # Supprimer la conversation
    conversation.delete()
    return redirect('chat_page')


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Vérifier si l'utilisateur est le sender ou le recipient du message
    if request.user != message.sender and request.user != message.recipient:
        return HttpResponseForbidden("You are not allowed to delete this message.")

    # Supprimer le message
    message.delete()
    return redirect('chat_page')
