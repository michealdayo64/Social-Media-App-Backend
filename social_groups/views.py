from django.shortcuts import render

# Create your views here.

def group_list(request):

    return render(request, 'group_list.html')

def group_detail(request, id):
    
    return render(request, 'group_detail.html')
