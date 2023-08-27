from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm,Userform
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
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context= {'rooms' : rooms , 'topics':topics, 'room_count': room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context )


def room(request,pk ):
    # room = None
    room=Room.objects.get(id=pk) 
    room_message=room.message_set.all().order_by('-created')
    participants=room.participants.all()
    # for i in rooms:
    #     if i['id']==int(pk) :
    #         room=i

    if request.method == 'POST':
        room_message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)


    context={'room':room,'room_message':room_message,'participants':participants}
    return render(request,'base/room.html',context)


def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages = user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

## this is to create ROOM
@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics=Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form=RoomForm(request.POST)
        # if form.is_valid():
        #     room=form.save(commit=False)
        #     room.host=request.user
        #     room.save()
        return redirect('HOME')
        
    context = {'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

## To update room and text inside it
@login_required(login_url='/login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics=Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("you are not allowed to update this room")
    
    if request.method=='POST':
        topic_name=request.POST.get("topic")
        topic,created=Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST.get("name") 
        room.topic=topic
        room.description=request.POST.get("description") 
        room.save()
        return redirect('HOME')
    
    

    context={'form':form,'topics':topics}
    return render(request,'base/room_form.html', context)


@login_required(login_url='/login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("you are not allowed to delete this room")
    
    if request.method=='POST':
        room.delete()
        return redirect('HOME')
    return render(request,'base/room_delete.html',{'object':room})



@login_required(login_url='/login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("you are not allowed to delete this room")
    
    if request.method=='POST':
        message.delete()

        return redirect('HOME')
    return render(request,'base/room_delete.html',{'object':message} )


@login_required(login_url='/login')
def updateUser(request):
    user=request.user
    form=Userform(instance=user)
    if request.method=='POST':
        form=Userform(request.POST,instance=user)
        if form.is_valid:
            form.save()
            return redirect('user-profile',user.id )

    return render(request,'base/update-user.html',{'form':form})
