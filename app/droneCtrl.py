from fastapi import APIRouter
from urllib.parse import urljoin
from datetime import datetime
from fastapi_utils.cbv import cbv
import threading
import requests
import random
import time
import os

drone_router = APIRouter()

@cbv(drone_router)
class DroneView:
    def __init__(self):
        self.drone = drone

    @drone_router.get("/command/refuel/{id}")
    def refuelDrone(self, id:str):
        #refuel command from COMMAND
        if self.drone.state == "UNLOADED":
            print(f"drone {id} refuelling initiated")
            time.sleep(1)
            print(f"drone {id} refuelling completed")
            self.drone.fuel = 100
            self.drone.state = "LOADING"
            if (self.drone.coord_x,self.drone.coord_y) == self.drone.destinationTwo:
                self.drone.destination = self.drone.destinationOne
            else:
                self.drone.destination = self.drone.destinationTwo
            self.drone.stop_signal.clear()
            self.drone.deliveryThread()
    
    @drone_router.get("/command/retire/{id}")
    def retireDrone(self, id:str):
        #retire command from COMMAND
        if self.drone.state == "UNLOADED":
            print(f"drone {id} shutdown initiated")
            time.sleep(1)
            print(f"drone {id} shutdown completed")
            self.drone.state = "SHUTDOWN"
            self.drone.sendTelemetry(False)
            return {"message": f"Drone {id} shutdown"}  

    @drone_router.get("/command/restart/{id}")
    def restartDrone(self, id:str):
        #restart command from COMMAND
        if self.drone.state == "SHUTDOWN":
            print(f"drone {id} startup initiated")
            time.sleep(1)
            print(f"drone {id} startup completed")
            self.drone.fuel = 100
            self.drone.state = "LOADING"
            if (self.drone.coord_x,self.drone.coord_y) == self.drone.destinationTwo:
                self.drone.destination = self.drone.destinationOne
            else:
                self.drone.destination = self.drone.destinationTwo
            self.drone.stop_signal.clear()
            self.drone.deliveryThread()

    @drone_router.get("/command/retry/{id}")
    def retryDrone(self, id:str):
        #retry command from COMMAND
        self.drone.sendTelemetry(True, True)

    @drone_router.get("/command/crash/{id}")
    def crashDrone(self, id:str):
        #simulate crash command from COMMAND
        print('Drone crashed')
        os._exit(0)
        


class Drone:
    def __init__(self):
        self.coord_x = 1
        self.coord_y = 0
        self.coord_z = 0
        self.fuel = 100
        self.state = "LOADING"
        self.drone_id = 1
        self.mode = "AUTO"
        self.destinationOne = (1,0)
        self.destinationTwo = (4,7)
        self.destination = self.destinationTwo
        self.base_url = "http://127.0.0.1:8000"
        self.client = requests.Session()
        print("THIS IS A NEW INSTANCE")
        self.stop_signal = threading.Event()
        self.deliveryThread()

    def deliveryThread(self):
        self.delivery_thread = threading.Thread(target=self.startDelivery, daemon=True)
        self.delivery_thread.start()

    def liftoff(self):
        print('drone loading initiated')
        self.sendTelemetry(False)
        time.sleep(1)
        print('cargo loaded')
        print('drone liftoff initiated')
        self.state = "LIFTOFF"
        self.sendTelemetry(False)
        time.sleep(1)
        self.coord_z += 1

    def landing(self):
        print('drone landing initiated')
        time.sleep(1)
        self.state = "LANDING"
        self.sendTelemetry(False)
        self.coord_z -= 1

    def flightPathOne(self):
        for i in range(4):
            time.sleep(1)
            self.coord_y += 1
            self.fuel -= 10
            self.sendTelemetry()

        for j in range(3):
            time.sleep(1)
            self.coord_x += 1
            self.fuel -= 10
            self.sendTelemetry()

        for k in range(3):
            time.sleep(1)
            self.coord_y += 1
            self.fuel -= 10
            if k != 2:
                self.sendTelemetry()

    def flightPathTwo(self):
        for i in range(3):
            time.sleep(1)
            self.coord_y -= 1
            self.fuel -= 10
            self.sendTelemetry()

        for j in range(3):
            time.sleep(1)
            self.coord_x -= 1
            self.fuel -= 10
            self.sendTelemetry()

        for k in range(4):
            time.sleep(1)
            self.coord_y -= 1
            self.fuel -= 10
            if k != 3:
                self.sendTelemetry()

    def deliverCargo(self):
        self.state = "DELIVERING"
        if self.destination == self.destinationTwo:
            self.flightPathOne()
        else:
            self.flightPathTwo()
        self.checkArrive()
        
    def checkArrive(self):
        #Check if drone has arrived at destination
        if (self.coord_x,self.coord_y) == self.destination:
            self.landing()
            self.state = "UNLOADING"
            print("Cargo has arrived, unloading initiated")
            self.sendTelemetry(False)
            self.state = "UNLOADED"
            print("Cargo has unloaded, standing by for next command...")
            self.sendTelemetry(False)
            self.stop_signal.set()

    def introSuboptimal(self, flag: bool):
        #Introduce signal loss
        if flag:
            prob = random.uniform(0, 1)
            if prob > 0.3:
                return True
        return False

    def connectCmd(self):
        #GET request to Command
        url = urljoin(self.base_url, f"/connect/{self.drone_id}")
        try:
            response = self.client.get(url)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"Server returned {e.response.status_code}"}

    def sendTelemetry(self,flag: bool = True, retry_flag: bool = False):
        #POST request to Command
        current_datetime = datetime.now()
        if retry_flag:
            dest = f'/retry_telemetry/{self.drone_id}'
        else:
            dest = f'/telemetry/{self.drone_id}'
        #url = urljoin(self.base_url, f"/telemetry/{self.drone_id}")
        url = urljoin(self.base_url, dest)
        payload = {'drone_id': self.drone_id, 'mode': self.mode, 'coordinate_x': self.coord_x, 'coordinate_y': self.coord_y, 'coordinate_z': self.coord_z, 'fuel': self.fuel, 'state': self.state, 'timestamp': str(current_datetime)}
        outcome = self.introSuboptimal(flag)
        if not outcome:
            try:
                response = self.client.post(url, json=payload)
                response.raise_for_status() 
                return response.json()
            except requests.exceptions.HTTPError as e:
                return {"error": f"Server returned {e.response.status_code}"}
        print("signal lost")  

    # main code
    def startDelivery(self):  
        while not self.stop_signal.is_set():      
            self.connectCmd()
            self.liftoff()
            self.deliverCargo()
        print("Delivery ended")
            
drone = Drone()





    




