from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Path to custom world
    world_file = os.path.join(
        get_package_share_directory('my_worlds'),
        'worlds',
        'line_world.world'
    )

    # Gazebo launch file
    gazebo_launch = os.path.join(
        get_package_share_directory('gazebo_ros'),
        'launch',
        'gazebo.launch.py'
    )

    # TurtleBot3 model
    turtlebot3_model = os.environ.get('TURTLEBOT3_MODEL', 'waffle_pi')

    # SDF file path
    sdf_file = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'models',
        f'turtlebot3_{turtlebot3_model}',
        'model.sdf'
    )

    # Ensure Gazebo can find TurtleBot3 models
    os.environ["GAZEBO_MODEL_PATH"] = os.environ.get("GAZEBO_MODEL_PATH", "") + ":" + \
                                      os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'models')

    return LaunchDescription([
        # Launch Gazebo with custom world
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([gazebo_launch]),
            launch_arguments={'world': world_file}.items(),
        ),

        # Spawn TurtleBot3 after 5 seconds delay
        TimerAction(
            period=5.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'ros2', 'run', 'gazebo_ros', 'spawn_entity.py',
                        '-entity', 'turtlebot3',
                        '-file', sdf_file,
                        '-x', '1.0',
                        '-y', '1.9',
                        '-z', '0.05'
                    ],
                    output='screen'
                )
            ]
        ),
    ])
