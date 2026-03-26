import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class QubePidController(Node):
    def __init__(self):
        super().__init__('qube_pid_controller')

        self.declare_parameter('joint_name', 'motor_joint')
        self.declare_parameter('reference', 0.0)
        self.declare_parameter('kp', 3.0)
        self.declare_parameter('ki', 0.0)
        self.declare_parameter('kd', 0.2)
        self.declare_parameter('max_command', 5.0)

        self.joint_name = self.get_parameter('joint_name').value
        self.reference = float(self.get_parameter('reference').value)
        self.kp = float(self.get_parameter('kp').value)
        self.ki = float(self.get_parameter('ki').value)
        self.kd = float(self.get_parameter('kd').value)
        self.max_command = float(self.get_parameter('max_command').value)

        self.position = None
        self.velocity = 0.0

        self.integral = 0.0
        self.prev_time = self.get_clock().now()

        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Float64MultiArray,
            '/velocity_controller/commands',
            10
        )

        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info('Qube PID controller started')

    def joint_state_callback(self, msg: JointState):
        if self.joint_name not in msg.name:
            return

        idx = msg.name.index(self.joint_name)

        if idx < len(msg.position):
            self.position = msg.position[idx]

        if idx < len(msg.velocity):
            self.velocity = msg.velocity[idx]
        else:
            self.velocity = 0.0

    def control_loop(self):
        if self.position is None:
            return

        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds * 1e-9
        self.prev_time = now

        if dt <= 0.0:
            return

        error = self.reference - self.position
        self.integral += error * dt
        derivative = -self.velocity

        command = self.kp * error + self.ki * self.integral + self.kd * derivative
        command = max(min(command, self.max_command), -self.max_command)

        msg = Float64MultiArray()
        msg.data = [command]
        self.cmd_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = QubePidController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()