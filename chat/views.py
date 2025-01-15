from django.shortcuts import render, redirect
from django.db import connections
from .models import Room, Message
from django.db import IntegrityError, connections
from django.db import connection
import logging
logger = logging.getLogger(__name__)


def HomeView(request):
    if request.method == "POST":
        if 'admin' in request.POST:
             return render(request, "admin.html")
        elif 'user' in request.POST:
            return render(request, "user.html")
        
    return render(request, "index.html")






def RoomView(request, room_name, username):
    try:
        # Fetch messages for the room from the chat_message table
        with connections['test'].cursor() as cursor:
            cursor.execute(
                "SELECT id, message, sender, timestamp FROM chat_message WHERE room_name_db = %s ORDER BY timestamp ASC",
                [room_name]  # room_name is the room_id
            )
            messages = cursor.fetchall()

        # Format messages for rendering
        formatted_messages = [
            {
                "id": message[0],
                "message": message[1],
                "sender": message[2],
                
            }
            for message in messages
        ]

        # Context for rendering the template
        context = {
            "messages": formatted_messages,
            "user": username,
            "room_name": room_name,  # room_name is directly used as room_id
        }

        return render(request, "room.html", context)
    except Exception as e:
        return render(request, "index.html", {"error_message": str(e)})




def join_room(request):
    """
    Handles user requests to join an existing chat room.
    """
    if request.method == "POST":
        # Retrieve user inputs
        username = request.POST.get("username", "").strip()
        room_name = request.POST.get("chatRoomName", "").strip()

        # Check for empty fields
        if not username or not room_name:
            return render(request, 'user.html', {
                'error': "Both Username and Chat Room Name are required."
            })

        # Log the inputs for debugging purposes
        print(f"Username: {username}, Room Name: {room_name}")

        with connections['test'].cursor() as cursor:
            try:
                # Check if the chat room exists in the database
                cursor.execute("SELECT * FROM admin WHERE room_name = %s", [room_name])
                room = cursor.fetchone()

                if room:
                    # Room exists - allow the user to join
                    cursor.execute("""
                    INSERT INTO users (username)
                    VALUES (%s) """, [username])
                  
                    return redirect('room', room_name= room_name, username = username)

                else:
                    # Room does not exist
                    return render(request, 'user.html', {
                        'error': f"The chat room '{room_name}' does not exist. Please check the name and try again."
                    })
            except Exception as e:
                # Handle unexpected database errors
                return render(request, 'user.html', {
                    'error': f"An error occurred while processing your request: {str(e)}"
                })

    # Render the form for GET requests
    return render(request, 'user.html')

 


def create_room(request):
    if request.method == "POST":
        # Retrieve and clean form data
        admin_Name = request.POST.get("adminName", "").strip()
        room_name = request.POST.get("chatRoomName", "").strip()

        # Basic validation for empty fields
        if not admin_Name or not room_name:
            return render(request, 'admin.html', {
                'error': "Both Admin Name and Room Name are required."
            })
        
        # Log the input for debugging
        print(f"Admin Name: {admin_Name}, Room Name: {room_name}")

        # Check if the room_name already exists in the database
        with connections['test'].cursor() as cursor:
            cursor.execute("SELECT * FROM admin WHERE room_name = %s", [room_name])
            existing_room = cursor.fetchone()

            if existing_room:
                # Room name already exists, return an error message
                return render(request, 'admin.html', {
                    'error': f"The room name '{room_name}' is already in use. Please choose a different name."
                })

            try:
                # Attempt to insert the room details into the database
                cursor.execute("""
                    INSERT INTO admin (admin_Name, room_name)
                    VALUES (%s, %s)
                """, [admin_Name, room_name])
                
                return redirect('room', room_name= room_name, username = admin_Name)
                
            
                
            

            except IntegrityError as e:
                # Handle duplicate entry or other integrity errors
                return render(request, 'admin.html', {
                    'error': f"An error occurred while creating the room: {str(e)}"
                })

            except Exception as e:
                # Handle unexpected errors
                return render(request, 'admin.html', {
                    'error': f"An unexpected error occurred: {str(e)}"
                })
    
    # Render the form for GET requests or if no POST request is made
    return render(request, 'admin.html')




