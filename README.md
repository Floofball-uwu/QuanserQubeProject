# Quanser Qube Project

This repository contains source code for controlling a Quanser Qube Servo 2 using a PID controller by utilizing ROS2. It is assumed that the Quanser Qube Servo 2 is controlled by an Arduino with appropiate software that allows to control the Qube through the `qube_driver`. The `qube_driver` source code is taken from [github.com/adamleon/qube_driver](https://github.com/adamleon/qube_driver).

URDF files are included for visualizing the Qube.

**<!> This project was tested on Ubuntu, and thus may not work on Windows. <!>**

# Packages
The project is split up into 4 packages.

### qube_description
Contains the macro description of the Qube itself, alongside a `joint_state` publisher. This package contains a launch file to quickly check if the visualization is correct.

### qube_controller
Contains the PID controller itself. This package contains a single node and no launch file. 

Publishes to `/velocity_controller/commands` of type `Float64MultiArray`. 

Subscribes to `/joint_states`, using its `position` and `velocity`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| joint_name | String | `motor_joint` | Name of joint to control |
| kp | float | `1` |Coefficient for P |
| ki | float | `0` | Coefficient for I |
| kd | float | `1` | Coefficient for D |
| reference | float | `0` |Reference for error. Target position. |
| max_velocity | float | `500` |Absolute maximum velocity controller will output. Values near 20 will fail to make Qube move. |


### qube_driver
The driver that allows to establish communication with the hardware. Subscribes to `/velocity_controller/commands` of type `Float64MultiArray`. 

For details, see [github.com/adamleon/qube_driver](https://github.com/adamleon/qube_driver)

### qube_bringup
Bundles everything together. This is where the launch file you want to use is located.

Creates a scene with XACRO that contains the URDF of the `qube_driver` alongside `qube_description`, and connects them together.

Additional parameters when launching this file are provided, which modify the XACRO parameters:
| Parameter | XACRO Type | Default | Description |
| --- | --- | --- | --- |
| baud_rate | unsigned int | `115200` | Baud rate for hardware communication. This must match with what the device supports. |
| device | String | `none` | USB device to connect to. On Linux it should look something like `/dev/ttyACMx`, where `x` is a number, usually 0. Run `ls /dev/tty*` to check. Full read/write permissions are preferred to avoid issues, so run `sudo chmod 666 /dev/ttyACMx`.|

# Launching the project
The launch file of interest is located in the `qube_bringup` package, named `bringup.launch.py`.

For a quick simulation, run:

`ros2 launch qube_bringup bringup.launch.py kp:=1.0 ki:=0 kd:=0.5 reference:=2 simulation:=true`.

For a physical test, run:

`ros2 launch qube_bringup bringup.launch.py kp:=30.0 ki:=0 kd:=2 reference:=0 device:=/dev/ttyACM0 simulation:=false`.

Note that the PID coefficients are different for the simulation. That is because the simulation does not model the motor nor inertia of the disk. 

The real example will make the motor feel like a torsion spring when you "wind up" the disk.

# Pipeline

**TODO: Write properly, preferably make figure**
**Node -> Topic -> Node -> Topic -> Node**