from django.shortcuts import render
from . models import Category
from publications.models import Publication
# Create your views here.
def category(request):
    return render(request, 'categories/category.html')
def categories(request):
    publications= Publication.objects.all()
    categories =Category.objects.all()
    context = {
        'categories': categories,
        'publications': publications
    }
    return render(request, 'categories/categories.html', context)

def health(request):
    publications= Publication.objects.all()
    categories =Category.objects.all()
    context = {
        'categories': categories,
        'publications': publications
    }
    return render(request, 'categories/health.html', context)

def education(request):
    publications= Publication.objects.all()
    categories =Category.objects.all()
    context = {
        'categories': categories,
        'publications': publications
    }
    return render(request, 'categories/education.html', context)

def environment(request):
    publications= Publication.objects.all()
    categories =Category.objects.all()
    context = {
        'categories': categories,
        'publications': publications
    }
    return render(request, 'categories/environment.html', context)

def children(request):
    publications= Publication.objects.all()
    categories =Category.objects.all()
    context = {
        'categories': categories,
        'publications': publications
    }
    return render(request, 'categories/children.html', context)

def urgent(request):
    publications= Publication.objects.all()
    categories =Category.objects.all()
    context = {
        'categories': categories,
        'publications': publications
    }
    return render(request, 'categories/urgent.html', context)