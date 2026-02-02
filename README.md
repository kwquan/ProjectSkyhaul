# Project Skyhaul
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/ProjectSkyhaul.png)

This repo contains the code used for Project Skyhaul, a backend project built to simulate a autonomous delivery drone and it's interactions with a command centre.

# Environment
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/gridworld.png)

Drone alternates delivery between points A and B in a 8x8 gridworld. Drone starts with state "LOADING" follows transition below:
"LOADING" > "LIFTOFF" > "DELIVERY". \
Upon reaching destination grid, it follows the transition below:
"LANDING" > "UNLOADING" > "UNLOADED" \

# Prerequisites
1. Copy paste app folder to desired directory
2. pip install dependencies in requirements.txt to virtual environment
3. Postgresql installed with server "postgreSQL 18"

# Steps[In VSCode] 
1. Run setupdb.py to create "telemetry" table. Change username and password to desired.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/create_database.png)
2. Open up 2 terminals
3. First terminal is for commandMain.py. Run "uvicorn app.commandMain:app --reload". This listens for API requests sent to the command centre and responds accordingly.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/command_running.png)
4. Second terminal is for droneMain.py. Run " uvicorn app.droneMain:app --reload --port 8001". This listens for API requests sent to the drone and responds accordingly.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/drone_running.png)
5. Note that drone will immediately start delivery upon running the above. Query telemetry table to verify that data has been sent from drone to command.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/query_1.png)
   
   

   

