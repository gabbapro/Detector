"""
Detector.py

Author		Version		Date		Comments
------------------------------------------------------------------------------------
Gabba		0.1		2019 02 06	Initial Version
Gabba		0.2		2019 03 04	Bug Fix + New Path Drive
Gabba   0.3   2019 03 12  Trim the number of photos, upload the photos in a specified OCI Object Storage bucket

"""

# Imports

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
import time
import sys
import os
import oci
import glob
from oci.object_storage.models import CreateBucketDetails

# Global Vars
directory = '.'
liveCamera = False
compartment_id = "ocid1.compartment.oc1..aaaaaaaadgkz352ghmiydawau7qua5gld2nxosmv5m6tmues6tavqvr22vla"
bucket_name = "Cracks"

def on_new_camera_image(evt, **kwargs):
    global liveCamera
    if liveCamera:
        pilImage = kwargs['image'].raw_image
        global directory
        pilImage.save(f"./images/{directory}-{kwargs['image'].image_number}.jpeg", "JPEG")

def shoot_sequence(robot: cozmo.robot.Robot):
    robot.set_head_angle(degrees(10.0)).wait_for_completed()
    take_photos(robot)
    robot.set_head_angle(degrees(20.0)).wait_for_completed()
    take_photos(robot)
    robot.set_head_angle(degrees(30.0)).wait_for_completed()
    take_photos(robot)
    robot.set_head_angle(degrees(40.0)).wait_for_completed()
    take_photos(robot)

def take_photos(robot: cozmo.robot.Robot):
    global liveCamera
    liveCamera = True
    time.sleep(0.05)
    liveCamera = False
    time.sleep(0.05)

def upload():
    print("----------------------------------------")    
    print("Detecting files in images directory.")
    print("Here's what I found:")
    print(glob.glob("./images/*.jpeg"))
    print("----------------------------------------")

    config = oci.config.from_file()
    object_storage = oci.object_storage.ObjectStorageClient(config)
    namespace = object_storage.get_namespace().data

    fileList = glob.glob("./images/*.jpeg")
    for currentFile in fileList:
        print (currentFile)
        with open(currentFile, 'rb') as f:
            obj = object_storage.put_object(namespace, bucket_name, os.path.basename(currentFile), f)

    print("Writing Termination File")
    open('Terminate.txt', 'a').close()
    with open('Terminate.txt', 'rb') as f:
        obj = object_storage.put_object(namespace, bucket_name, 'Terminate.txt', f)

def cozmo_program(robot: cozmo.robot.Robot):
    # Reset head 
    robot.set_head_angle(degrees(0.0)).wait_for_completed()
    # Reset lift 
    robot.set_lift_height(0.0).wait_for_completed()
    # Announce activity
    robot.say_text("Stage 1").wait_for_completed()

    # Create images directory if it doesn't exists
    global directory
    directory = sys.argv[1]
    if not os.path.exists('images'):
        os.makedirs('images')

    # Drive to 1st Location
    robot.drive_straight(distance_mm(340), speed_mmps(90), False, False, 0).wait_for_completed()
    # Initialise Camera
    take_photos(robot)
    # new image == new pic
    robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)
    shoot_sequence(robot)

    # Announce activity
    robot.say_text("Stage 2").wait_for_completed()

    # Drive to 2nd Location
    robot.drive_straight(distance_mm(-50), speed_mmps(90), False, False, 0).wait_for_completed()
    robot.turn_in_place(degrees(90)).wait_for_completed()
    robot.drive_straight(distance_mm(250), speed_mmps(90), False, False, 0).wait_for_completed()
    robot.turn_in_place(degrees(-90)).wait_for_completed()
    robot.drive_straight(distance_mm(300), speed_mmps(90), False, False, 0).wait_for_completed()
    robot.turn_in_place(degrees(-90)).wait_for_completed()
    robot.drive_straight(distance_mm(230), speed_mmps(90), False, False, 0).wait_for_completed()
    robot.turn_in_place(degrees(-90)).wait_for_completed()
    robot.drive_straight(distance_mm(50), speed_mmps(90), False, False, 0).wait_for_completed()
    # new image == new pic
    robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)
    shoot_sequence(robot)

    upload()

    #  And we're done here
    robot.say_text("Images sent to Oracle Cloud").wait_for_completed()

cozmo.run_program(cozmo_program, use_viewer=True, force_viewer_on_top=True)
