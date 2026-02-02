# Project Skyhaul
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/ProjectSkyhaul.png)

This repo contains the code used for Project Skyhaul, a backend project built to simulate a autonomous delivery drone and it's interactions with a command centre.

# Prerequisites
1. Copy paste all files in app folder to desired directory
2. pip install dependencies in requirements.txt to virtual environment
3. Postgresql installed with server "postgreSQL 18"

# Steps[In VSCode] 
1. Run setupdb.py to create "telemetry" table. Change username and password to desired.
2. Open up 2 terminals
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/command_running.png)
3. First terminal is for commandMain.py. Run "uvicorn app.commandMain:app --reload". This listens for API requests sent to the command centre and responds accordingly.
![alt text](https://github.com/kwquan/ProjectSkyhaul/blob/main/images/drone_running.png)
4. Second terminal is for droneMain.py. Run " uvicorn app.droneMain:app --reload --port 8001". This listens for API requests sent to the drone and responds accordingly.
5. Note that drone will immediately start delivery upon running the above.
   

   

