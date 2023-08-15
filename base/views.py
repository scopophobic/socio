from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm
# Create your views here.


# rooms = [
#     {'id':1, 'name': 'lets learn python'},
#     {'id':2, 'name': 'you are amazing'},
#     {'id':3, 'name': 'design an app'},
# ]

def loginPage(request):
    page="login"
    if request.user.is_authenticated:
        return redirect('HOME')
    if request.method=="POST":
        username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try:
            user= User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist')

        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect ('HOME')
        else:
            messages.error(request,'Username or Password Does not match')
    
    context={'page':page}
    return render(request,'base/login_register.html', context)

def logoutPage(request):
    logout(request)
    return redirect('HOME')

def registerPage(request):
    page="register"
    form=UserCreationForm()
    context={'page':page, 'form':form}

    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False) 
            user.username=user.username.lower()
            user.save()
            login(request, user)
            return redirect('HOME')
        else:
            messages.error(request,'error try again')
    return render(request,'base/login_register.html',context)

def home (request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    topics=Topic.objects.all()
    room_count=rooms.count()
    context= {'rooms' : rooms , 'topics':topics, 'room_count': room_count}
    return render(request,'base/home.html',context )


def room(request,pk ):
    # room = None
    room=Room.objects.get(id=pk) 
    # for i in rooms:
    #     if i['id']==int(pk) :
    #         room=i
    
    context={'room':room}
    return render(request,'base/room.html',context)



## this is to create ROOM
@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()

    if request.method=='POST':
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('HOME')
        
    context = {'form':form}
    return render(request,'base/room_form.html',context)

## To update room and text inside it
@login_required(login_url='/login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)


    if request.user != room.host:
        return HttpResponse("you are not allowed to update this room")
    
    if request.method=='POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid:
            form.save()
            return redirect('HOME')
    
    

    context={'form':form}
    return render(request,'base/room_form.html', context)


@login_required(login_url='/login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("you are not allowed to delete this room")
    
    if request.method=='POST':
        room.delete()
        return redirect('HOME')
    return render(request,'base/room_delete.html',{'obj':room})
