"""
main.py
"""
# Change the default path below or pass as argument
CSV_FILE_DEFAULT_PATH = '/home/sheng/Projects/robodk_xray/csv_files/Example-XYZWPR-Duration_simple.csv'

import os
import argparse

# robodk API
from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robomath import *  # Robot toolbox
from robodk.robodialogs import *
from robodk.robofileio import *

# Declare ROBOT and RDK as global variables
# Start communication with RoboDK
RDK = Robolink()

# Ask the user to select the robot (ignores the popup if only
ROBOT = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

# Check if the user selected a robot
if not ROBOT.Valid():
    quit()

# Automatically retrieve active reference and tool
FRAME = ROBOT.getLink(ITEM_TYPE_FRAME)
TOOL = ROBOT.getLink(ITEM_TYPE_TOOL)

#FRAME = RDK.ItemUserPick('Select a reference frame', ITEM_TYPE_FRAME)
#TOOL = RDK.ItemUserPick('Select a tool', ITEM_TYPE_TOOL)

if not FRAME.Valid() or not TOOL.Valid():
    raise Exception("Select appropriate FRAME and TOOL references")

def parse_args():
    '''
    Pass arguments of the csv file path when calling the python script. 
    '''
    parser = argparse.ArgumentParser(description="A RoboDK project")
    parser.add_argument("--csv_file", 
                        default=CSV_FILE_DEFAULT_PATH, 
                        type=str, help="Path to the CSV file")
    args = parser.parse_args()
    return args

# Function to convert XYZWPR to a pose
# Important! Specify the order of rotation
def xyzwpr_to_pose(xyzwpr):
    x, y, z, rx, ry, rz = xyzwpr
    return transl(x, y, z) * rotz(rz * pi / 180) * roty(ry * pi / 180) * rotx(rx * pi / 180)
    #return transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    #return KUKA_2_Pose(xyzwpr)

def load_task(csv_file): 
    codec = 'utf-8'  #'ISO-8859-1'
    csvdata = LoadList(csv_file, ',', codec)
    tasks = [] # tasks is a list of dictionary
    for i in range(0, len(csvdata)):
        x, y, z, rx, ry, rz = csvdata[i][0:6]
        duration = csvdata[i][6]
        tasks.append({
            "pose": xyzwpr_to_pose([x, y, z, rx, ry, rz]),
            "duration": duration
        })
    print(f"Loaded {len(tasks)} tasks from {csv_file}!")
    return tasks

def TurnXrayBeamOn(beam_on):
    # TO-DO: set x-ray beam IO to true
    pass

def _execute_task_GUI(tasks): 
    program_name = (args.csv_file)
    program_name = program_name.replace('-', '_').replace(' ', '_')
    program = RDK.Item(program_name, ITEM_TYPE_PROGRAM)
    if program.Valid():
        program.Delete()
    program = RDK.AddProgram(program_name, ROBOT)
    program.setFrame(FRAME)
    program.setTool(TOOL)
    ROBOT.MoveJ(ROBOT.JointsHome())

    for i, task in enumerate(tasks):
        name = '%s-%i' % (program_name, i)
        target = RDK.Item(name, ITEM_TYPE_TARGET)
        if target.Valid():
            target.Delete()
        target = RDK.AddTarget(name, FRAME, ROBOT)
        target.setPose(task["pose"])
        
        try: 
            program.MoveJ(target)
        except: 
            print('Warning: %s can not be reached. It will not be added to the program' % name)
        TurnXrayBeamOn(True)
        pause(task["duration"] / 1000.0)    # ms to s
        TurnXrayBeamOn(False)

def _execute_task_move(tasks):
    ROBOT.setFrame(FRAME)
    ROBOT.setTool(TOOL)

    ROBOT.MoveJ(ROBOT.JointsHome())
    for i, task in enumerate(tasks):
        try: 
            ROBOT.MoveJ(task["pose"])
        except:
            RDK.ShowMessage('Target %i can not be reached' % i, False)
        TurnXrayBeamOn(True)
        pause(task["duration"] / 1000.0)    # ms to s
        TurnXrayBeamOn(False)

def execute_task(tasks):
    '''
    Execute the tasks for the ROBOT
    '''
    MAKE_GUI_PROGRAM = False

    ROBOT.setFrame(FRAME)
    ROBOT.setTool(TOOL)

    if RDK.RunMode() == RUNMODE_SIMULATE:
        MAKE_GUI_PROGRAM = True
        # MAKE_GUI_PROGRAM = mbox('Do you want to create a new program? If not, the robot will just move along the tagets', 'Yes', 'No')
    else:
        # if we run in program generation mode just move the robot
        MAKE_GUI_PROGRAM = False

    MAKE_GUI_PROGRAM = False

    if MAKE_GUI_PROGRAM:
        print("debug 1")
        RDK.Render(False)  # Faster if we turn render off
        _execute_task_GUI(tasks)
    else:
        print("debug 2")
        _execute_task_move(tasks)

def run():
    tasks = load_task(args.csv_file)
    execute_task(tasks)

if __name__ == "__main__":
    args = parse_args()
    run()