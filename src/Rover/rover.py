from pymavlink import mavutil
from ..Camera import *
import time
import math

class Rover:
    def __init__(self,roverSerial,connection):
        vehicle = mavutil.mavlink_connection(connection)
        vehicle.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (vehicle.target_system, vehicle.target_component))

        _ = vehicle.messages.keys() #All parameters that can be fetched

        pos = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        system = vehicle.recv_match(type='SYS_STATUS', blocking=True)

        self.serial=roverSerial
        self.lat=pos.lat * 10e-8
        self.lon=pos.lon * 10e-8
        self.battery=system.battery_remaining
        self.vehicle=vehicle
        self.workingStatus=False
        self.camera = Camera()
        self.droneSerial="ERROR000000000"
        self.droneStatus="Free"
        self.roverStatus="Free"

    def changeVehicleMode(self,mode):
        print("Changing vehicle mode to",mode)
        # Get mode ID
        mode_id = self.vehicle.mode_mapping()[mode]
        # Set new mode

        self.vehicle.mav.set_mode_send(
            self.vehicle.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id)
        msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)
        print(msg)


    def setupAndArm(self):
        self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

        self.vehicle.mav.command_long_encode(
		0, 0,
		mavutil.mavlink.MAV_CMD_DO_SET_REVERSE,
		0,
		1,
		0,
		0,
		0,
		0,0, 0)

        self.vehicle.mav.command_long_encode(
		0, 0,
		mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
		0,
		30,
		0,
		0,
		0,
		0,0, 0)

    def moveForward(self, speed):
        self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                        self.vehicle.target_component, mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, int(0b110111000111), 0, 0, 0, speed, 0, 0, 0, 0, 0, 0, 0))

    def moveBackward(self, speed):
        self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                        self.vehicle.target_component, mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, int(0b11011100111), 0, 0, 0, -(speed), 0, 0, 0, 0, 0, 0, 0))
    
    def moveForward_L(self, speed, d=0):
        system = self.vehicle.recv_match(type='LOCAL_POSITION_NED', blocking=True)

        initial = system.x
        current = initial
        self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                        self.vehicle.target_component, mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, int(0b110111000110), d, 0, 0, speed, 0, 0, 0, 0, 0, 0, 0))
        
        while True:
            change = abs(abs(initial) - abs(current))
            if change >= 5:
                break
            self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                        self.vehicle.target_component, mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, int(0b110111000110), d, 0, 0, speed, 0, 0, 0, 0, 0, 0, 0))
            system = self.vehicle.recv_match(type='LOCAL_POSITION_NED', blocking=True)
            current = system.x
            print('current head', current)
            print('change head',change)
            
        

    def moveBackward_L(self, speed, d=0):
        self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                        self.vehicle.target_component, mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, int(0b11011100110), d, 0, 0, -(speed), 0, 0, 0, 0, 0, 0, 0))

    def changeYaw(self, angle, speed=0):

        system = self.vehicle.recv_match(type='ATTITUDE', blocking=True)
        print(angle) # Correct angle by adding abs difference in 180 degrees
        initial = math.degrees(system.yaw)
        current = initial
        self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                        self.vehicle.target_component, mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED , int(0b100111100111), 0, 0, 0, (speed), 0, 0, 0, 0, 0, angle, 0))
        
        while True:
            change = abs(abs(initial) - abs(current))
            if change >= 90:
                break
            self.vehicle.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, self.vehicle.target_system,
                        self.vehicle.target_component, mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED , int(0b100111100111), 0, 0, 0, (speed), 0, 0, 0, 0, 0, angle, 0))
            system = self.vehicle.recv_match(type='ATTITUDE', blocking=True)
            current = math.degrees(system.yaw)
            print('current head', current)
            print('change head',change)
            

if __name__== "__main__":
    pass