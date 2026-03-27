import os
from ament_index_python import * 
import xacro

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, TextSubstitution

#Launch command:
#ros2 launch qube_bringup bringup.launch.py kp:=30.0 ki:=0 kd:=2 reference:=0 device:=/dev/ttyACM0 simulation:=false

def launch_setup(context, *args, **kwargs):
    #Parsing the launch file parses XACRO too, instead it has to be after arguments are resolved
    #For consistency, do this thing for all parameters
    #However, this makes them default to strings, requiring casting where necessary!
    baud_rate = LaunchConfiguration("baud_rate").perform(context)
    device = LaunchConfiguration("device").perform(context)
    simulation = LaunchConfiguration("simulation").perform(context)
    kp = LaunchConfiguration("kp").perform(context)
    ki = LaunchConfiguration("ki").perform(context)
    kd = LaunchConfiguration("kd").perform(context)
    reference = LaunchConfiguration("reference").perform(context)
    max_velocity = LaunchConfiguration("max_velocity").perform(context)

    #Load the "scene" file
    xacroFile = os.path.join(get_package_share_directory("qube_bringup"), "urdf/controlled_qube.urdf.xacro")
    #Apply launch parameters and process into XML
    robot_description_content = xacro.process_file(xacroFile,
        mappings = 
        {
            "baud_rate": baud_rate, #A number, but in xacro it is a string
            "device": device, #String
            "simulation": str(simulation).lower(), #Protect against uppercase
        }
        ).toxml()

    #Load another launch file. Launcheption!
    qubeDriver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("qube_driver"), "launch/qube_driver.launch.py")
        )
    )

    rviz = Node(
            package="rviz2",
            executable="rviz2",
            #load rviz setup config
            arguments = [ "-d", [os.path.join(get_package_share_directory("qube_bringup"), "config/config.rviz")]]
        )

    robotState = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description_content}] #load urdf
        )
    
    pidController = Node(
            package='qube_controller',
            executable='pid_controller',
            parameters=[{
            "kp": float(kp),
            "ki": float(ki),
            "kd": float(kd),
            "reference": float(reference),
            "max_velocity": float(max_velocity)
            }]
        )
    
    nodes = [
        qubeDriver,
        rviz, 
        robotState,
        pidController
    ]

    return nodes

#This generates the launch description itself
def generate_launch_description():
    launchArgs = [
        DeclareLaunchArgument("baud_rate", default_value="115200"),
        DeclareLaunchArgument("device", default_value="none"),
        DeclareLaunchArgument("simulation", default_value="false"),
        DeclareLaunchArgument("kp", default_value="1"),
        DeclareLaunchArgument("ki", default_value="0"),
        DeclareLaunchArgument("kd", default_value="1"),
        DeclareLaunchArgument("reference", default_value="0"),
        DeclareLaunchArgument("max_velocity", default_value="500"),
    ]

    #Which returns these arguments alongside a properly parsed launch file alongside xacro
    #The result is a convinient and easy way to change parameters!
    return LaunchDescription(launchArgs + [OpaqueFunction(function=launch_setup)])