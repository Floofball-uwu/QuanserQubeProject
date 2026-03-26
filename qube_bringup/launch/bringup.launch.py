import os
from ament_index_python import * 
import xacro

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, TextSubstitution

def launch_setup(context, *args, **kwargs):
    #Parsing the launch file parses XACRO too, instead it has to be after arguments are resolved
    #For consistency, do this thing for all parameters
    baud_rate  = LaunchConfiguration("baud_rate").perform(context)
    device     = LaunchConfiguration("device").perform(context)
    simulation = LaunchConfiguration("simulation").perform(context)
    kp         = LaunchConfiguration("kp").perform(context)
    ki         = LaunchConfiguration("ki").perform(context)
    kd         = LaunchConfiguration("kd").perform(context)
    reference  = LaunchConfiguration("reference").perform(context)

    #Load the "scene" file
    xacroFile = os.path.join(get_package_share_directory("qube_bringup"), "urdf/controlled_qube.urdf.xacro")
    #Apply launch parameters and process into XML
    robot_description_content = xacro.process_file(xacroFile,
        mappings = 
        {
            "baud_rate":  baud_rate,
            "device":     device,
            "simulation": simulation,
        }
        ).toxml()

    qubeDriver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("qube_driver"), "launch/qube_driver.launch.py")
        )
    )

    rviz = Node(
            package="rviz2",
            executable="rviz2",
            arguments = [ "-d", [os.path.join(get_package_share_directory("qube_bringup"), "config/config.rviz")]]
        )

    robotState = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description_content}] # adds a URDF to the robot description
        )
    
    pidController = Node(
            package='qube_controller',
            executable='pid_controller',
            parameters=[{
            "kp":        kp,
            "ki":        ki,
            "kd":        kd,
            "reference": reference,
            }]
        )
    
    nodes = [
        qubeDriver,
        rviz, 
        robotState,
        pidController
    ]

    return [qubeDriver, rviz, robotState, pidController]

def generate_launch_description():
    launchArgs = [
        DeclareLaunchArgument("baud_rate",  default_value="115200"),
        DeclareLaunchArgument("device",     default_value="none"),
        DeclareLaunchArgument("simulation", default_value="true"),
        DeclareLaunchArgument("kp",         default_value="1"),
        DeclareLaunchArgument("ki",         default_value="0"),
        DeclareLaunchArgument("kd",         default_value="1"),
        DeclareLaunchArgument("reference",  default_value="0"),
    ]

    return LaunchDescription(launchArgs + [OpaqueFunction(function=launch_setup)])