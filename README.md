# Project Skyhaul
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/ProjectSkyhaul.png)

This repo contains the code used for Project Skyhaul, a backend project built to simulate a autonomous delivery drone and it's interactions with a command centre.

# Description
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/gridworld.png)

Drone alternates delivery between points A and B in a 8x8 gridworld. \
Drone starts with state "LOADING" follows transition below: \
"LOADING" > "LIFTOFF" > "DELIVERY" \
Upon reaching destination grid, it follows the transition below: \
"LANDING" > "UNLOADING" > "UNLOADED" \
Once destination is reached, command can either: 
1) refuel drone: upon which drone continues it's next delivery 
2) retire drone: upon which drone is shutdown and awaits command to restart

# Notes

Drone starts sending telemetry every second when it starts delivering. \
However, there is a chance this DOES NOT occur[to simulate real-life signal loss events]. \
When command does not receive telemetry data[fulfilling certain conditions], it will send \
a command requesting telemetry data to drone[up to 3 times] before notifying recovery team[assumes that drone has crashed]

# Prerequisites
1. Copy paste app folder to desired directory
2. pip install dependencies in requirements.txt to virtual environment
3. Postgresql installed with server "postgreSQL 18"

# Steps[In VSCode] [delivery]
1. Run setupdb.py to create "telemetry" table. Change username and password to desired.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/create_database.png)
2. Open up 2 terminals
3. First terminal is for commandMain.py. Run "uvicorn app.commandMain:app --reload". This listens for API requests sent to the command centre and responds accordingly.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/command_running.png)
4. Second terminal is for droneMain.py. Run " uvicorn app.droneMain:app --reload --port 8001". This listens for API requests sent to the drone and responds accordingly.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/drone_running.png)
5. Note that drone will immediately start delivery upon running the above. Query telemetry table to verify that data has been sent from drone to command.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/query_1.png)
6. Upon reaching destination, command can either refuel drone(refer to steps 7x) or retire drone(refer to steps 8x)

IF refuel: \
7a. In command terminal, enter 'refuel' when prompted
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/select_refuel_command.png)
7b. Observe that drone starts it's next delivery
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/select_refuel_drone.png)
7c. Verify that next delivery's data is sent to telemetry table
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/query_2.png)

IF retire: \
8a. In command terminal, enter 'retire' when prompted
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/select_retire_command.png)
8b. Observe that drone shuts down
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/select_retire_drone.png)
8c. For next prompt in command terminal, if 'y' is entered, drone restarts and starts new delivery
8d. Verify that next delivery's data is sent to telemetry table. Note the SHUTDOWN state of drone prior to restarting.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/query_3.png)




# Steps 
   
   

   

