# xz_motion_mechanism_sim

这是一个面向 X-Z 两自由度运动机构仿真的 ROS Noetic / Gazebo Classic 模型包。

模型来源于 STEP 装配体。包内保留了两类模型：

- STEP 导出的 STL 网格，用于 RViz/Gazebo 外观预览。
- 两自由度 URDF 仿真模型，视觉使用分组 STL，物理碰撞暂时简化/关闭，便于先验证运动关系和控制接口。

## 目录内容

- `package.xml`：ROS 包信息。
- `CMakeLists.txt`：catkin 构建和安装规则。
- `urdf/xz_motion_mechanism.urdf`：Gazebo/ros_control 两自由度模型。
- `urdf/xz_motion_mechanism_step_visual.urdf`：完整 STEP 外观的 RViz 静态预览模型。
- `launch/gazebo_sim.launch`：启动 Gazebo 并生成模型，不加载控制器。
- `launch/gazebo_2dof.launch`：启动 Gazebo，可选加载控制器。
- `launch/sim_with_joint_gui.launch`：启动 Gazebo、控制器和关节滑条 GUI。
- `launch/joint_command_gui.launch`：单独启动关节滑条 GUI。
- `launch/display_2dof.launch`：在 RViz 中预览两自由度模型。
- `meshes/base_visual.stl`：固定基座和支架外观。
- `meshes/x_stage_visual.stl`：X 轴运动组件外观。
- `meshes/y_stage_visual.stl`：Z 轴运动组件外观。
- `meshes/grouped_meshes_manifest.txt`：当前 STEP 零件分组清单。
- `scripts/convert_step_with_freecad.py`：用 FreeCAD 从 STEP 导出完整 STL。
- `scripts/export_grouped_step_meshes.py`：用 FreeCAD 按分组规则导出三段 STL。

## 推荐安装方式：catkin 工作空间

把本包放到任意 catkin 工作空间的 `src` 目录下，例如：

```bash
mkdir -p ~/catkin_ws/src
cp -r xz_motion_mechanism_sim ~/catkin_ws/src/
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

之后 ROS 会自动找到这个包：

```bash
rospack find xz_motion_mechanism_sim
```

如果希望每个新终端自动生效，可以加入 `~/.bashrc`：

```bash
echo 'source /opt/ros/noetic/setup.bash' >> ~/.bashrc
echo 'source ~/catkin_ws/devel/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

## 不构建时的使用方式

如果只是把包放在某个普通目录中，也可以不运行 `catkin_make`。这时需要让 `ROS_PACKAGE_PATH` 指向“包所在的父目录”。

假设目录结构是：

```text
<package_parent>/xz_motion_mechanism_sim
```

则执行：

```bash
source /opt/ros/noetic/setup.bash
export ROS_PACKAGE_PATH=<package_parent>:$ROS_PACKAGE_PATH
```

例如包在 `~/models/xz_motion_mechanism_sim`，则：

```bash
export ROS_PACKAGE_PATH=~/models:$ROS_PACKAGE_PATH
```

同样可以写入 `~/.bashrc`：

```bash
echo 'source /opt/ros/noetic/setup.bash' >> ~/.bashrc
echo 'export ROS_PACKAGE_PATH=<package_parent>:$ROS_PACKAGE_PATH' >> ~/.bashrc
source ~/.bashrc
```

把 `<package_parent>` 换成你自己的实际路径。

## Gazebo 模型路径

通过本包的 ROS launch 启动时，通常不需要手动设置 `GAZEBO_MODEL_PATH`，因为 URDF 里的网格使用 `package://xz_motion_mechanism_sim/...` 路径。

如果你想在 Gazebo 的 Insert 面板中直接看到这个模型，或者直接加载 `model.sdf` / `model_step_visual.sdf`，需要让 `GAZEBO_MODEL_PATH` 指向包所在的父目录：

```bash
export GAZEBO_MODEL_PATH=<package_parent>:$GAZEBO_MODEL_PATH
```

如果 ROS 已经能找到包，也可以自动推导：

```bash
PKG_ROOT=$(rospack find xz_motion_mechanism_sim)
export GAZEBO_MODEL_PATH=$(dirname "$PKG_ROOT"):$GAZEBO_MODEL_PATH
```

## 启动仿真

启动 Gazebo、模型、控制器和滑条控制 GUI：

```bash
roslaunch xz_motion_mechanism_sim sim_with_joint_gui.launch
```

只启动 Gazebo 和模型，不加载控制器：

```bash
roslaunch xz_motion_mechanism_sim gazebo_sim.launch
```

启动 Gazebo 和控制器，不启动滑条 GUI：

```bash
roslaunch xz_motion_mechanism_sim gazebo_2dof.launch controllers:=true gui:=true
```

单独启动滑条 GUI：

```bash
roslaunch xz_motion_mechanism_sim joint_command_gui.launch
```

## 控制话题

控制器启动后，两个位置控制话题为：

```bash
/xz_motion_mechanism/x_axis_position_controller/command
/xz_motion_mechanism/y_axis_position_controller/command
```

示例：

```bash
rostopic pub -1 /xz_motion_mechanism/x_axis_position_controller/command std_msgs/Float64 "data: 0.25"
rostopic pub -1 /xz_motion_mechanism/y_axis_position_controller/command std_msgs/Float64 "data: 0.10"
```

## RViz 预览

预览两自由度分组模型，并用滑条移动关节：

```bash
roslaunch xz_motion_mechanism_sim display_2dof.launch
```

预览完整 STEP 静态外观：

```bash
roslaunch xz_motion_mechanism_sim display_step_visual.launch
```

## 生成姿态参数

默认 Gazebo 生成姿态：

```text
spawn_z:=0.41
spawn_roll:=-1.57079632679
```

如果模型方向需要微调，可以在启动时覆盖：

```bash
roslaunch xz_motion_mechanism_sim gazebo_2dof.launch spawn_z:=0.40 spawn_roll:=-1.57079632679
```

## 重新生成 STL

重新导出完整静态 STL：

```bash
cd <package_root>/scripts
freecadcmd convert_step_with_freecad.py <path_to_step_file> ../meshes/module_visual.stl
```

重新按当前分组规则导出两自由度 STL：

```bash
cd <package_root>/scripts
freecadcmd export_grouped_step_meshes.py <path_to_step_file> ../meshes
```

其中：

- `<package_root>` 是 `xz_motion_mechanism_sim` 包目录。
- `<path_to_step_file>` 是你的 STEP 文件路径。

导出的 STL 单位是毫米。URDF/SDF 中使用 `scale="0.001 0.001 0.001"` 转成米，并使用测得的 STEP 整体中心 `(347.488, 369.008, 590.000) mm` 做坐标居中。

## 当前运动关系

```text
world --fixed--> base_link --x_axis_joint--> x_stage_link --y_axis_joint--> y_stage_link
```

- `base_link`：固定底座、门架支架、横梁、固定导轨、横向长齿条和滚轮滑座。
- `x_stage_link`：相对横向长齿条运动的盒盖/滑座组件，包含顶部导轨滑块、电机、齿轮、执行机构连接件和盒盖等。
- `y_stage_link`：竖向齿条，作为相对盒盖组件运动的第二自由度部件。
- `x_axis_joint`：X 向直线关节，默认行程 `-0.50` 到 `0.50` m。
- `y_axis_joint`：Z 向直线关节的仿真接口，当前 URDF 内部名称仍为 `y_axis_joint`，默认行程 `-0.24` 到 `0.24` m。

## 建模说明

- 视觉模型来自 STEP 分组网格，尽量保持真实外观。
- 当前两自由度调试模型暂时关闭碰撞体，避免粗略 box 和地面/运动部件穿插导致 Gazebo 发抖。
- 基座通过 `world_to_base` 固定在 Gazebo 世界中，防止机构作为自由刚体在重力下翻倒。
- 两个自由度用 Gazebo 支持良好的 prismatic joint 表达，适合先完成机构仿真和控制联调。
- 如果后续需要表达齿轮-齿条啮合，可以在控制层建立位移-转角映射，或者增加 mimic/插件逻辑。
