from fastapi import status, APIRouter
import time
import psycopg2
import threading
import requests
from psycopg2.extras import RealDictCursor
from fastapi_utils.cbv import cbv
from pydantic import BaseModel
from datetime import datetime
from urllib.parse import urljoin

command_router = APIRouter()

class TelemetryData(BaseModel):
    drone_id : int
    mode : str
    coordinate_x : int
    coordinate_y : int
    coordinate_z: int
    fuel: int
    state: str
    timestamp: datetime


@cbv(command_router)
class CommandView:
    def __init__(self):
        self.command = command

    @command_router.get("/connect/{id}")
    def connectDrone(self, id:str):
        print(f"drone {id} connection established!")
        return {"message": f"Drone {id} connected"}    
    
    @command_router.post("/telemetry/{id}", status_code = status.HTTP_201_CREATED)
    def teleDrone(self, id:str, telemetry: TelemetryData):
        self.command.cursor.execute("""INSERT INTO telemetry (drone_id, mode, coordinate_x, coordinate_y, coordinate_z, fuel, state, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""", 
                   (telemetry.drone_id, telemetry.mode, telemetry.coordinate_x, telemetry.coordinate_y, telemetry.coordinate_z, telemetry.fuel, telemetry.state, telemetry.timestamp))
     
        self.command.conn.commit()
        print(f"drone {id} telemetry received!")
        self.command.checkArrive(telemetry.coordinate_x, telemetry.coordinate_y, telemetry.coordinate_z, telemetry.state)
        return {"message": f"Drone {id} telemetry sent"}
    
    @command_router.post("/retry_telemetry/{id}", status_code = status.HTTP_201_CREATED)
    def retryDrone(self, id:str, telemetry: TelemetryData):
        self.command.cursor.execute("""INSERT INTO telemetry (drone_id, mode, coordinate_x, coordinate_y, coordinate_z, fuel, state, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""", 
                   (telemetry.drone_id, telemetry.mode, telemetry.coordinate_x, telemetry.coordinate_y, telemetry.coordinate_z, telemetry.fuel, telemetry.state, telemetry.timestamp))
     
        self.command.conn.commit()
        self.command.status = "OPTIMAL"
        self.command.retry_received = True
        print(f"drone {id} connection reestablished!")
        return {"message": f"Drone {id} retry telemetry sent"}


class Command:
    def __init__(self):
        self.connectDB()
        self.last_received = None
        self.status = "OPTIMAL"
        self.destinationOne = (1,0,0)
        self.destinationTwo = (4,7,0)
        self.destination = self.destinationTwo
        self.base_url = "http://127.0.0.1:8001"
        self.drone_id = 1
        self.retry_received = False
        self.client = requests.Session()
        self.stop_signal = threading.Event()
        self.monitorThread()

    def monitorThread(self):
        if hasattr(self, 'checker_thread') and self.checker_thread.is_alive():
            print("Monitor thread is already running.")
            return
        self.checker_thread = threading.Thread(target=self.updateStatusReceived, daemon=True)
        self.checker_thread.start()

    def connectDB(self):
        while True:
            try:
                self.conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
                                    password='12345', cursor_factory=RealDictCursor)
                self.cursor = self.conn.cursor()
                print("Command Database connection established!")
                break
            except Exception as error:
                print("Connecting to Command Database failed")
                print("Error: ", error)
                time.sleep(2)

    def updateStatusReceived(self, id: str="1"):
        while not self.stop_signal.is_set(): 
            self.cursor.execute("""SELECT timestamp, state FROM telemetry
            WHERE drone_id = %s ORDER BY timestamp DESC LIMIT 1""", (str(id)))
            latest_received = self.cursor.fetchone()
            if latest_received and (latest_received['state'] in ['LIFTOFF','DELIVERING']):
                latest_time = latest_received['timestamp']
                time_diff = datetime.now() - latest_time
                if time_diff.total_seconds() > 0:
                    self.status = "OPTIMAL"
                if time_diff.total_seconds() > 2:
                    self.status = "SUBOPTIMAL"
                if time_diff.total_seconds() > 5:
                    self.status = "SIGNALLOSS"
                    for i in range(3):
                        time.sleep(1)
                        self.retryConnection()
                        if self.retry_received:
                            break 
                    if not self.retry_received:
                        print("SIGNALLOSS: NOTIFY RECOVERY TEAM")
                        self.simulateCrash()
                        return

                print(f"CURRENT STATUS: {self.status}")
                time.sleep(1)
        print("End of status monitoring")

    def checkArrive(self, coord_x, coord_y, coord_z, state):
        if ((coord_x, coord_y, coord_z) == self.destination) and (state == "UNLOADED"):
            self.refuelRetire()

    def refuelRetire(self):
        print("Drone has arrived. Enter next command('refuel/retire'):")
        command = input().lower()
        self.stop_signal.set()
        self.checker_thread.join()
        while command not in ["refuel", "retire"]:
            print("Invalid command, try again")
            command = input().lower()
        if command == "refuel":
            self.refuelDrone()
            return
        if command == "retire":
            self.retireDrone()
            self.restartDrone()
            return
        return

    def refuelDrone(self):
        #GET refuel request to DRONE
        print("Refuelling drone...")
        if hasattr(self, 'checker_thread'):
            self.checker_thread.join(timeout=2.0) 
        if self.destination == self.destinationTwo:
            self.destination = self.destinationOne
        else:
            self.destination = self.destinationTwo
        time.sleep(1)
        self.status = "OPTIMAL"
        self.stop_signal.clear()
        self.monitorThread()
        url = urljoin(self.base_url, f"/command/refuel/{self.drone_id}")
        try:
            response = self.client.get(url)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as e:
                return {"error": f"Server returned {e.response.status_code}"}
    
    def retireDrone(self):
        #GET retire request to DRONE
        url = urljoin(self.base_url, f"/command/retire/{self.drone_id}")
        try:
            response = self.client.get(url)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"Server returned {e.response.status_code}"}
        
    def restartDrone(self):
        #GET restart request to DRONE
        print("Standing by to start delivery. Enter command('y'):")
        command = input().lower()
        while command != "y":
            print("Invalid command, try again")
            command = input().lower()
        if command == "y":
            print("Restarting drone...")
            if self.destination == self.destinationTwo:
                self.destination = self.destinationOne
            else:
                self.destination = self.destinationTwo
            time.sleep(1)
            self.status = "OPTIMAL"
            self.stop_signal.clear()
            self.monitorThread()
            url = urljoin(self.base_url, f"/command/restart/{self.drone_id}")
            try:
                response = self.client.get(url)
                response.raise_for_status() 
                return response.json()
            except requests.exceptions.HTTPError as e:
                return {"error": f"Server returned {e.response.status_code}"}
            
    def retryConnection(self):
        #GET retry request to DRONE  
        url = urljoin(self.base_url, f"/command/retry/{self.drone_id}")
        try:
            response = self.client.get(url)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"Server returned {e.response.status_code}"}
        
    def simulateCrash(self):
        #GET simulate crash request to DRONE  
        url = urljoin(self.base_url, f"/command/crash/{self.drone_id}")
        try:
            response = self.client.get(url)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"Server returned {e.response.status_code}"}
        

        
command = Command()
        

