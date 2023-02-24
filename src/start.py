from .Rover import *
from src.dock import dock


def mainStart(serial=None, connection=None):
    if serial != None:
        print(serial)
        rover = Rover(roverSerial=serial,connection=connection)
        dock(rover=rover)

if __name__ == '__main__':
    pass
else:
    mainStart()