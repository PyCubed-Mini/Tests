print('Initializing PyCubed Hardware...')
# most hardware connectivity checks are done within 
# the pycubedmini library when pocketqube is initialized
from pycubedmini import pocketqube as cubesat
from debugcolor import co
import time

reading_error = False

# taken from beepsat advanced task file
def debug(msg,level=1):
    """
    Print a debug message formatted with the task name and color

    :param msg: Debug message to print
    :param level: > 1 will print as a sub-level

    """
    name = 'temp'
    color = 'gray'

    if level==1:
        print('{:>30} {}'.format('['+co(msg=name,color=color)+']',msg))
    else:
        print('{}{}'.format('\t   └── ',msg))


def main_task() :
    # get readings
    readings = {
                'accel': cubesat.acceleration,
                'mag':  cubesat.magnetic,
                'gyro': cubesat.gyro,
            }

    # store them in our cubesat data_cache object
    cubesat.data_cache.update({'imu':readings})

    # print the readings with some fancy formatting
    debug('IMU readings (x,y,z)')
    for imu_type in cubesat.data_cache['imu']:
        debug('{:>5} {}'.format(imu_type,cubesat.data_cache['imu'][imu_type]),2)

    # test readings
    for (key, val) in readings.items():
        for v in val:
            errcount = 0
            if v == 0:
                errcount += 1
            if errcount == 3:
                # print error message and exit
                print(key, "has all 0 values. Check sensor.\n")
                return False  # return with error
    
    return True

def imu_test():
    reading_error = False
    while(not reading_error):
        time.sleep(5);
        reading_error = not main_task()




