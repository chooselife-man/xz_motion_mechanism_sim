cmake_minimum_required(VERSION 3.0.2)
project(xz_motion_mechanism_sim)

find_package(catkin REQUIRED)
catkin_package()

install(DIRECTORY config launch rviz urdf meshes
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(PROGRAMS
  scripts/joint_command_gui.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
