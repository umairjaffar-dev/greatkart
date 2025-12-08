from .models import Category

##  - Make a context_processor function and add it in a setting.py templates context then it will be
#   accessable in all templates across the project.

def menu_links(request):
    links = Category.objects.all()
    
    return dict(links=links)