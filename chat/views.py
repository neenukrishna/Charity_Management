# from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.contrib.auth.decorators import login_required

@login_required
def chat_room(request, room_name):
    return render(request, 'chat/chat.html', {'room_name': room_name})


@login_required
def generic_chat_room(request, room_name):
    return render(request, 'chat/chat.html', {'room_name': room_name})

from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def user_list(request):
    # For admin: list all users except the current one.
    # Adjust this if you want a different filtering for non-admin users.
    if not request.user.is_staff:
        return redirect('chat_room', other_id=request.user.id)
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/user_list.html', {'users': users})

@login_required
def chat_room(request, other_id):
    # Get the user we are chatting with.
    other_user = get_object_or_404(User, id=other_id)
    current_id = request.user.id
    # Create a room name by sorting the two user IDs.
    room_ids = sorted([str(current_id), str(other_id)])
    room_name = "_".join(room_ids)
    return render(request, 'chat/chat.html', {'room_name': room_name, 'other_user': other_user})