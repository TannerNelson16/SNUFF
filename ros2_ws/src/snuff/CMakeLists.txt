cmake_minimum_required(VERSION 3.8)
project(snuff)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(apriltag_msgs REQUIRED)

install(
    DIRECTORY
      launch/
    DESTINATION share/${PROJECT_NAME}/launch
)

install(
    DIRECTORY
      rviz/
    DESTINATION share/${PROJECT_NAME}/rviz
)

install(
    DIRECTORY
      config/
    DESTINATION share/${PROJECT_NAME}/config
)

install(
    DIRECTORY
      models/
    DESTINATION share/${PROJECT_NAME}/models
)
install(
    DIRECTORY
      worlds/
    DESTINATION share/${PROJECT_NAME}/worlds
)

# Install Python modules
ament_python_install_package(${PROJECT_NAME})
# Install Python executables
install(PROGRAMS
#scripts/command.py
scripts/exec.py
scripts/state_publisher.py
DESTINATION lib/${PROJECT_NAME}
)



ament_package()
