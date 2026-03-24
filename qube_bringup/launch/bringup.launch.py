import os
from ament_index_python import * 
import xacro

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    xacroFile = os.path.join(get_package_share_directory("qube_bringup"), "urdf/controlled_qube.urdf.xacro")
    robot_description_content = xacro.process_file(xacroFile).toxml()

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
    
    nodes = [
        qubeDriver,
        rviz, 
        robotState
    ]

    return LaunchDescription(nodes)