import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class SimpleJointPublisher(Node):
    def __init__(self):
        super().__init__('simple_joint_publisher')

        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.05, self.publish_joint_state)
        self.t = 0.0

    def publish_joint_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['disk_joint']
        msg.position = [0.8 * math.sin(self.t)]
        self.publisher_.publish(msg)
        self.t += 0.05


def main(args=None):
    rclpy.init(args=args)
    node = SimpleJointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()