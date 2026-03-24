import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    xacro_file = os.path.join(
        get_package_share_directory("qube_description"),
        "urdf",
        "qube.urdf.xacro"
    )

    robot_description_content = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([
        Node(
            package="qube_description",
            executable="simple_joint_publisher",
            name="simple_joint_publisher",
            output="screen",
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description_content}],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
        ),
    ])