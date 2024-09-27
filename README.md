# Redis Chatroom

This Redis Chatbot is a console-based chat application for real-time messaging and user management. The chatbot offers public and private messaging, user profiles, channel management, and interactive commands.

## Key Features:

* User Management: Users can create profiles, delete profiles, and view information about other users.
* Channel Operations: Users can join channels, leave channels, and list available channels.
* Messaging: The application supports both public channel messages and private user-to-user messaging.
* Real-time Updates: Messages are delivered in real-time using Redis pub/sub functionality.
* Interactive Commands: Users can access information store in the database through special commands (e.g., !weather, !fact, !list_my_channels) as well as interact with the chatbot to get assistance (eg. !help, !delete_profile).


## How to run:

1. Clone the repository

```bash
git clone https://github.com/isabelarvelo/redis-chatroom.git
cd redis-chatroom
```


2. Run the following command to build the docker image. This will use the docker-compose.yml file to build the image and run the container:

```bash
docker-compose up
```

3. Open a new terminal (in the same folder) and run the following command to run the chatbot script from within the docker container:

```bash
docker-compose exec python bash
```

If this is your first time running the chatbot and you want to have sample data to test the chatbot functionalities, run the following command to populate the database with sample data:

```bash
python populate_weather.py
python populate_facts.py
```
Note: The !weather and !fact commands will only work if you run these commands to populate the database with sample data.

4. Once inside the container, run the following command to start the chatbot:

```bash
python redis_chatroom.py 
```

5. Once the chatbot is running, you can follow the instructions on the screen to interact with the chatbot. You can create a profile, join channels, send messages, and use the interactive commands to get information from the database.

6. To exit the chatbot, type `!exit` and press enter. To stop the docker container, open a new terminal and run the following command:

```bash
docker-compose down
```

7. If you want to delete all of the data in the Redis database, run the following command:

**Use with caution! This will delete all of the data in the Redis database and you cannot recover any information deleted using this method.**

```bash
python flush_keys.py
```

## Technologies Used:

- Python
- Redis
- Docker


## References:

I got the ASCII art from an [ASCII art archive](https://www.asciiart.eu/computers/computers). 

I used the following websites to help me gather fun facts:
https://sustainability-success.com/environmental-sustainability-fun-facts/
https://www.factretriever.com/giant-panda-facts
https://www.factretriever.com/vegetarian-facts
https://ftw.usatoday.com/2015/04/best-101-sports-facts-trivia-crazy-amazing-incredible-babe-ruth-michael-phelps-michael-jordan
https://www.sciencefocus.com/science/fun-facts

These facts are to demonstrate the use of the chatbot and should be verified by the user before being used in any serious context.

Below are specific links for the documentation and external sources I used to help me with the project:
- [Intro to Python Threading](https://realpython.com/intro-to-python-threading/)
- [Threading in Python](https://superfastpython.com/threading-in-python/)
- [redis-py dev documentation](https://redis-py.readthedocs.io/en/stable/index.html)
- [Redis Pub/Sub In-Depth](https://medium.com/@joudwawad/redis-pub-sub-in-depth-d2c6f4334826)
- DS 5760 Brightspace Materials 


## Generative AI Usage:

I used Generative AI (Specifically [Claude Sonnet 3.5](https://www.anthropic.com/news/claude-3-5-sonnet) ) to help me set up the threading so that users can constantly listen for and see messages from any channel they are subscribed to while interacting with the chatbot. To validate the suggestion Claude provided for this functionality and demonstrate my understanding of the code in my submission, I have included my own explanation of how the threading works in my chatbot use case. I have also included a comment in the code to show where I used the threading.

A thread is a separate flow of execution that allows a program to run multiple sequences of instructions at the same time (technically only one thread can execute Python code at once, but to the user both things appear to be happening in tandem). Using the Python threading module, I create a thread and tell it to start when a user is identified. When creating the thread, I pass the listen_for_messages function as the target function to run in the background, while the main program continues to run. A daemon thread is one that will shut down immediately when the program exits. Since we are only interested in listening for messages while the chatbot is running, we set the daemon flag to True.

The listen_for_messages function will constantly run in the background and put any messages sent to the channels that the user is subscribed to into a message queue. It sleeps for 0.001 seconds between each iteration to avoid using too much CPU. Every message read from a PubSub instance will be a dictionary with the following keys: 'subscribe', 'unsubscribe', 'psubscribe', 'punsubscribe', 'message', 'pmessage'. We are specifically interested in messages, so we will only pay attention to messages of type 'message'. We can then parse the rest of the fields from the message object to display who it was sent from and on which channel it was sent. We then add the message to the message queue, which will be processed by the main program loop. Inside this loop, the program waits for user input using select.select() with a timeout of 0.1 seconds. If user input is received, it's processed based on the choice made (e.g., identifying user, joining channel, sending message, etc.). After processing the user's choice (or if no input was received within the 0.1-second timeout), the process_message_queue() method is called to check if there are any messages in the queue to display to the user. If there are messages, they are displayed to the user. This cycle repeats continuously until the user chooses to exit. This ultimately allows the message queue to be continuously monitored and processed without blocking the main user interaction loop.

The ideas for the additional functionalities were mine, and the majority of the code implementation was done by me using the class demos and discussions, Redis documentation, and Docker documentation as references. I used Docker containers in DS 5220 and previous cross-functional projects, so I was familiar with how to set up a Dockerfile and requirements.txt file.

I also used generative AI to proofread this README file and GitHub Copilot assisted me in creating docstrings for all of my functions. I take full responsibility for all work in this project, and can explain any part of the code in detail if needed.
