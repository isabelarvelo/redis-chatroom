import redis
import json
import random
import threading
import time
import queue
import select
import sys
import time

class RedisChatbot:
    """ 
    A chatbot that allows users to chat with each other in channels and send private messages
    """
    def __init__(self, host='my-redis', port=6379):
        # Connect to the Redis server
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        # Create a pubsub instance
        self.pubsub = self.client.pubsub()
        self.current_user = None
        self.listening = False
        # Create a queue to store messages
        self.message_queue = queue.Queue()

    def initialize(self):
        """ 
        Display the welcome message and list of commands
        """
        welcome_message = """
        _______________                        |*\_/*|________
    |  ___________  |     .-.     .-.      ||_/-\_|______  |
    | |           | |    .****. .****.     | |           | |
    | |   0   0   | |    .*****.*****.     | |   0   0   | |
    | |     -     | |     .*********.      | |     -     | |
    | |   \___/   | |      .*******.       | |   \___/   | |
    | |___     ___| |       .*****.        | |___________| |
    |_____|\_/|_____|        .***.         |_______________|
     _|___|/ \|___.............*.............._|________|_


    Welcome to the Redis Chatbot!

    Here are the commands you can use:
    !help: List of commands
    !weather <city>: Weather update
    !fact: Random fact
    !add_fact <fact>: Add a fact you find interesting
    !whoami: Your user information
    !users: List all users
    !delete_profile: Delete your user profile
    !list_my_channels: List all channels you are subscribed to
    !list_all_channels: List all channels available
    
    Options:
    1: Identify yourself
    2: Join a Channel
    3: Leave a Channel
    4: Send a message to a channel 
    5: Get info about a user
    6: Send a private message
    7: Exit

    Go forth and chat!

    If you ever lose your way, type !help to see this message again.

    """
        print(welcome_message)

    def identify_user(self):
        """ 
        Identify the user, set up their private inbox, and start listening for messages
        """

        # A user is able to identify themselves with a username.
        username = input("Enter your username: ")

        # Store user information, including their name, age, gender, and location
        age = input("Enter your age: ")
        gender = input("Enter your gender: ")
        location = input("Enter your location: ")
        join_date = time.strftime("%Y-%m-%d %I:%M:%S", time.localtime())

        user_key = f"user:{username}"
        self.client.hset(user_key, mapping={
            "name": username,
            "age": age,
            "gender": gender,
            "location": location, 
            "join_date": join_date
        })
        self.current_user = username

        # There is no natively implemented direct messaging in Redis, so we create a private channel is created for each user
        private_channel = f"{username} private inbox"
        self.client.sadd(f"channels:{self.current_user}", private_channel)

        # Each user automatically subscribes to their private channel
        self.pubsub.subscribe(private_channel)

        # Start listening for messages
        if not self.listening:
            self.listening = True
            # Create a new thread to listen for messages
            thread = threading.Thread(target=self.listen_for_messages)
            # Set the thread as a daemon so it will stop when the main thread stops
            thread.daemon = True
            # Start the thread
            thread.start()
        
        # Welcome message
        print(f"Welcome {username}! You have been identified and your private inbox has been set up.\n")

    def list_all_users(self):
        """ 
        List all users in the chatroom
        """
        user_keys = self.client.keys("user:*")
        
        if not user_keys:
            print("No users found.")
            return

        print("\nList of all users:")
        for user_key in user_keys:
            username = user_key.split(':')[1]  
            user_info = self.client.hgetall(user_key)
            print(f"- {username}")
            for key, value in user_info.items():
                if key != 'name':  
                    print(f"  {key.capitalize()}: {value}")
            print()  
    
    def delete_profile(self):
        """ 
        Allow the user to delete their profile
        """
        if not self.current_user:
            print("Please identify yourself first. Type 1 to identify yourself.\n")
            return

        confirm = input(f"Are you sure you want to delete your profile, {self.current_user}? This action cannot be undone. (yes/no): ")
        if confirm.lower() != 'yes':
            print("Profile deletion cancelled.\n")
            return

        # Delete the user's profile information
        user_key = f"user:{self.current_user}"
        self.client.delete(user_key)

        # Unsubscribe from all channels
        channels_key = f"channels:{self.current_user}"
        channels = self.client.smembers(channels_key)
        for channel in channels:
            self.pubsub.unsubscribe(channel)
        self.client.delete(channels_key)

        # Unsubscribe from the private channel
        private_channel = f"{self.current_user} private inbox"
        self.pubsub.unsubscribe(private_channel)

        print(f"Profile for {self.current_user} has been deleted.")
        self.current_user = None
        self.listening = False

    def join_channel(self):
        """ 
        Allow the user to join a channel
        """
        if not self.current_user:
            print("Please identify yourself first. Type 1 to identify yourself.\n")
            return
        
        # A user is able to join a channel by entering the channel name.
        channel = input("Enter the channel name to join: ")

        # The channel name is added to two sets: one for the user and to keep track of all channels
        self.client.sadd(f"channels:{self.current_user}", channel)
        self.client.sadd("channel_names", channel)

        # Function for user to actually subscribe to the channel
        self.pubsub.subscribe(channel)
        print(f"You've joined the channel: {channel}\n")
        

    def leave_channel(self):
        """ 
        Allow the user to leave a channel
        """
        if not self.current_user:
            print("Please identify yourself first. Type 1 to identify yourself.\n")
            return
        
        channel = input("Enter the channel name to leave: ")

        # Remove the channel from the user's set of channels
        self.client.srem(f"channels:{self.current_user}", channel)

        # Unsubscribe from the channel
        self.pubsub.unsubscribe(channel)

        # Notify the user that they have left the channel
        print(f"You've left the channel: {channel}")

    def send_message(self):
        """ 
        Allow the user to send a message to a channel
        """
        if not self.current_user:
            print("Please identify yourself first. Type 1 to identify yourself.\n")
            self.identify_user()
            return
        
        channel = input("Enter the channel name: ").strip()
        message = input("Enter your message: ").strip()
        
        # Format the message as a JSON object
        message_obj = {
            "from": self.current_user,
            "message": message
        }

        # Publish the message to the channel
        self.client.publish(channel, json.dumps(message_obj))

        # Add the channel to the list of all channels if it doesn't already exist in the set
        self.client.sadd("channel_names", channel)

        print(f"Message sent to channel {channel}")

        # If user not in channel, ask if they want to join
        if not self.client.sismember(f"channels:{self.current_user}", channel):
            join = input(f"You are not in the channel {channel}. Would you like to join? (yes/no): \n")
            if join.lower() == 'yes':
                self.client.sadd(f"channels:{self.current_user}", channel)
                self.pubsub.subscribe(channel)
                print(f"You've joined the channel: {channel}\n")
    

    def send_private_message(self):
        """ 
        Allow the user to send a private message to another user
        """
        if not self.current_user:
            print("Please identify yourself first. Type 1 to identify yourself.")
            return
        
        # A user is able to send a private message to another user by entering the recipient's username, which 
        # is also the name of the channel set up as the recipient's private inbox.

        recipient = input("Enter the username of the recipient: ")
        message = input("Enter your private message: ")
        
        recipient_channel = f"{recipient} private inbox"
        message_obj = {
            "from": self.current_user,
            "message": message,
            "private": True
        }
        
        # Publish the message to the recipient's private channel
        self.client.publish(recipient_channel, json.dumps(message_obj))
        
        print(f"Private message sent to {recipient}\n")

    def get_user_info(self):
        """ 
        Allow the user to get information about another user
        """
        username = input("Enter username to get info about: ")
        user_key = f"user:{username}"

        # Retrieve ther user information from the hash mapping
        user_info = self.client.hgetall(user_key)
        if user_info:
            print(f"Info for user {username}:\n")
            for key, value in user_info.items():
                print(f"{key.capitalize()}: {value}")
        else:
            print(f"No information found for user {username}")

    def add_fact(self, fact):
        """ 
        Allow the user to add a fact to the set of facts in the database. 
        """
        if not fact:
            print("Please provide a fact to add.")
            return
        
        # Add the fact to the set of facts
        self.client.sadd("facts", fact)
        print("\nFact added successfully! Other users can now learn from your wisdom.\n")


    def list_user_channels(self):
        """ 
        List all channels the user has joined
        """
        if not self.current_user:
            print("Please identify yourself first. Type 1 to identify yourself.\n")
            return
        
        # Get the set of channels the user has joined
        channels = self.client.smembers(f"channels:{self.current_user}")
        if channels:
            print("\nList of channels you've joined:")
            for channel in channels:
                print(f"- {channel}")
            print("\n")
        else:
            print("You haven't joined any channels yet.")
    
    def list_channels(self):
        """ 
        List all channels available
        """
        channels = self.client.smembers("channel_names")
        if channels:
            print("\nList of all channels:")
            for channel in channels:
                print(f"- {channel}")
            print("\n")
        else:
            print("No channels found.")
    

    def handle_special_commands(self, command):
        """ 
        Handle special commands that start with an exclamation
        """

        # Split the command into parts and call the appropriate function

        parts = command.split()
        if parts[0] == "!help":
            self.initialize()
        elif parts[0] == "!weather":
            city = " ".join(parts[1:])
            self.get_weather(city)
        elif parts[0] == "!fact":
            self.get_fact()
        elif parts[0] == "!whoami":
            self.get_whoami()
        elif parts[0] == "!users":
            self.list_all_users()
        elif parts[0] == "!delete_profile":
            self.delete_profile()
        elif parts[0] == "!add_fact":
            self.add_fact(" ".join(parts[1:]))
        elif parts[0] == "!list_my_channels":
            self.list_user_channels()
        elif parts[0] == "!list_all_channels":
            self.list_channels()
        else:
            print("Unknown command. Type !help for a list of commands.")

    def get_weather(self, city):
        """
        Get the weather for a specific city
        """
        if not city:
            print("Please provide a city name after the command. For example, !weather New York\n")
            return
        
        # lowercase the city name because the weather data is stored in lowercase
        city = city.lower()  
        weather = self.client.hget("weather", city)
        if weather:
            print(f"\nThe weather in {city.title()} is {weather}\n")
            return
        else:
            print(f"No weather information available for {city.title()}\n")
            return

    def get_fact(self):
        """ 
        Get a random fact from the set of facts
        """
        fact = self.client.srandmember("facts")
        if fact:
            print(f"\nDid you know? {fact}\n")
            return
        else:
            print("No facts available at the moment.")

    def get_whoami(self):
        """ 
        Get the user's information
        """
        if not self.current_user:
            print("Please identify yourself first. Type 1 to identify yourself.")
            return
        user_info = self.client.hgetall(f"user:{self.current_user}")
        if user_info:
            print("Your user information:\n")
            for key, value in user_info.items():
                print(f"{key.capitalize()}: {value}")
                print()
        else:
            print("No information found for your user.\n")

    def listen_for_messages(self):
        """
        Listen for messages from the pubsub channel
        """
        while self.listening:
            # Get the next message from the pubsub channel
            message = self.pubsub.get_message()

            # If the message is a message type, process the message
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                channel = message['channel']
                # If the message is private, only show it to the recipient, not the sender
                if (data.get('private', False) and (data['from'] != self.current_user)):
                    self.message_queue.put(f"\n{time.strftime('%I:%M:%S %p', time.localtime())} -- Private message from {data['from']}:\n{data['message']}\n")
                elif (data['from'] != self.current_user):
                    # Include the time the message was sent
                    self.message_queue.put(f"\n{time.strftime('%I:%M:%S %p', time.localtime())} -- Message in channel {channel}\nFrom: {data['from']}\n\n{data['message']}\n")
            else:
                time.sleep(0.001)

    def process_message_queue(self):
        """ 
        Process the message queue to display messages
        """

        # Check if there are messages in the queue and display them
        while not self.message_queue.empty():
            message = self.message_queue.get()
            print(message)
            sys.stdout.flush()

    def run(self):
        """ 
        Main loop to run the chatbot
        """
        self.initialize()
        try:
            while True:
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    choice = sys.stdin.readline().strip()
                    if choice.startswith("!"):
                        self.handle_special_commands(choice)
                    elif choice == "1":
                        self.identify_user()
                    elif choice == "2":
                        self.join_channel()
                    elif choice == "3":
                        self.leave_channel()
                    elif choice == "4":
                        self.send_message()
                    elif choice == "5":
                        self.get_user_info()
                    elif choice == "6":
                        self.send_private_message()  
                    elif choice == "7":
                        print("""
    ____                 _   _                _ 
    / ___| ___   ___   __| | | |__  _   _  ___| |
    | |  _ / _ \ / _ \ / _` | | '_ \| | | |/ _ \ |
    | |_| | (_) | (_) | (_| | | |_) | |_| |  __/_|
    \____|\___/ \___/ \__,_| |_.__/ \__, |\___(_)
                                    |___/        
                            """)
                        break
                    else:
                        print("Invalid choice. Please try again.")
                self.process_message_queue()
        finally:
            self.listening = False
            self.pubsub.close()

if __name__ == "__main__":
    chatbot = RedisChatbot()
    chatbot.run()


