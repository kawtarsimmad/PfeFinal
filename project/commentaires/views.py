from django.shortcuts import render,redirect,get_object_or_404
from .forms import CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from . models import Comment
from publications.models import Publication
from events.models import Event

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json 





@login_required
def create_comment(request, model_name, object_id):
    if model_name == 'publication':
        model = get_object_or_404(Publication, id=object_id)
    elif model_name == 'event':
        model = get_object_or_404(Event, id=object_id)
    else:
        return redirect('home')  # Redirige vers la page d'accueil ou une autre page appropriée

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.content_object = model
            comment.auteur = request.user
            comment.save()
            # Redirection vers la page de détail de la publication ou de l'événement
            if model_name == 'publication':
                return redirect('detail', pk=object_id)
            elif model_name == 'event':
                return redirect('detail_events', pk=object_id)
    else:
        form = CommentForm()

    context = {
        'form': form,
        'model': model
    }
    
    return render(request, 'comment_form.html', context)


@login_required
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user != comment.auteur:
        return redirect('/')  # Redirigez vers une vue appropriée

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
              # Redirigez vers la page de détail de l'objet commenté après la mise à jour
            if comment.content_type.model == 'publication':
                return redirect('detail', pk=comment.object_id)
            elif comment.content_type.model == 'event':
                return redirect('detail_events', pk=comment.object_id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'comment_form.html', {'form': form})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user != comment.auteur:
        return redirect('/')  # Redirigez vers une vue appropriée
    
    if request.method == 'POST':
        # Récupérer le modèle de contenu associé au commentaire
        content_type = ContentType.objects.get_for_model(comment.content_object)
        
        comment.delete()
        
        # Utiliser le modèle de contenu pour obtenir l'URL de détail appropriée
        if content_type.model == 'publication':
            return redirect('detail', pk=comment.object_id)
        elif content_type.model == 'event':
            return redirect('detail_events', pk=comment.object_id)
    
    return render(request, 'comment_confirm_delete.html', {'comment': comment})
