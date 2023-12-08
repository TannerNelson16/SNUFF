import os

from ament_index_python.packages import get_package_share_directory

from launch.actions import SetEnvironmentVariable
from launch_ros.actions import SetParameter
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription

from launch_ros.actions import Node

def generate_launch_description():
#    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    robot_path = get_package_share_directory('snuff')
#    gz_sim = IncludeLaunchDescription(
#        PythonLaunchDescriptionSource(
#            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
#        launch_arguments={'gz_args': '-r '+os.path.join(robot_path,'/models/world.sdf -s --headless-rendering')}.items(),
#        launch_arguments={'gz_args': '-r '+os.path.join(robot_path,'models/robot/world.sdf')}.items(),
#    )
    microros = Node(
        package='micro_ros_agent',
        executable = 'micro_ros_agent',
        name='micro_ros_agent',
        arguments=["udp4", "-p", "8888", "-v6"]
    )
    camera = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        parameters=[robot_path+"/config/params_1.yaml"]
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(robot_path, 
            'rviz', 'robot.rviz')],
    )

    apriltags = Node(
        package='apriltag_ros',
        executable='apriltag_node',
        remappings=[
            ('image_rect', '/image_raw'),
           # ('image_rect', '/camera'),
            ('camera_info', '/camera_info'),
        ],
        parameters=[robot_path+"/config/apriltags.yaml"]
    )

    # Load the SDF file from "description" package
    sdf_file  =  os.path.join(robot_path, 
        'models', 'robot', 'robot.sdf')
    with open(sdf_file, 'r') as infp:
        robot_desc = infp.read()


    # Takes the description and joint angles as inputs and publishes the 3D poses of the robot links
    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        arguments=['-d', os.path.join(robot_path,'models', 'robot','world.sdf')],
        output=['screen']
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'robot_description': robot_desc},
            {'use_sim_time': True},
        ]
    )


   # Bridge

    executive = Node(
        package='snuff',
        executable='exec.py',
        output='screen'        
    )

    state_publisher = Node(
        package='snuff',
        executable='state_publisher.py',
        output='screen'
    )
    flame_state_publisher = Node(
        package='snuff',
        executable='flame_state_publisher.py',
        output='screen'
    )
    object_found_sub = Node(
        package='snuff',
        executable='object_found_sub.py',
        output='screen'
    )


    return LaunchDescription([
        camera,
        microros,
#        apriltags,
        flame_state_publisher,
        object_found_sub,
        executive,
        state_publisher,
 #       rviz
        
    ])
