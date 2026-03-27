import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
from rclpy.qos import QoSProfile, ReliabilityPolicy


class QubePidController(Node):
    def __init__(self):
        super().__init__('qube_pid_controller')

        #Setup node parameters
        self.declare_parameter('joint_name', 'motor_joint')
        self.declare_parameter('reference', 0.0)
        self.declare_parameter('kp', 20.0)
        self.declare_parameter('ki', 0.0)
        self.declare_parameter('kd', 1.0)
        self.declare_parameter('max_velocity', 500.0)

        self.joint_name = self.get_parameter('joint_name').value
        self.reference = self.get_parameter('reference').get_parameter_value().double_value
        self.kp = self.get_parameter('kp').get_parameter_value().double_value
        self.ki = self.get_parameter('ki').get_parameter_value().double_value
        self.kd = self.get_parameter('kd').get_parameter_value().double_value
        self.max_velocity = self.get_parameter('max_velocity').get_parameter_value().double_value

        #Initialize values. Initial position and previous time unknown.
        self.position = None
        self.velocity = 0.0

        self.integral = 0.0
        self.prev_time = None

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

        #Start timer to call control loop callback
        self.timer = self.create_timer(0.0001, self.control_loop)

        self.get_logger().info('Qube PID controller started')
        return


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
        
        return


    #The PID control itself
    #Controls velocity to try keeping a constant position.
    def control_loop(self):
        if self.position is None: #Omit if position unknown
            return

        now = self.get_clock().now()

        if self.prev_time is None: #First frame will give have no previous time
            self.prev_time = now
            return

         #Get nanoseconds from Time object, then convert to seconds.
        dt = (now - self.prev_time).nanoseconds * 1e-9
        self.prev_time = now

        if dt <= 0.0:
            return

        error = self.reference - self.position #P, error
        self.integral += error * dt #I, error over time, accumulator
        derivative = -self.velocity #D, we already get velocity directly from the Qube interface

        command = self.kp * error + self.ki * self.integral + self.kd * derivative #P + I + D
        command = max(min(command, self.max_velocity), -self.max_velocity) #Clamp to [-max_velocity, max_velocity]

        #Send message
        msg = Float64MultiArray()
        msg.data = [command]
        self.cmd_pub.publish(msg)
        return


def main(args=None):
    rclpy.init(args=args)
    node = QubePidController()
    try:
        rclpy.spin(node)
    finally:
        #If an error occurs, stop motor and shut down
        msg = Float64MultiArray()
        msg.data = [0.0]
        node.cmd_pub.publish(msg)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()