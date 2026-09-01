# xz_motion_mechanism_sim

这是一个从 `/home/hyf/Documents/model.STEP` 转换整理出来的 ROS/Gazebo 模型包。

原始 STEP 文件是 SolidWorks 2022 AP214 装配体，装配名称为 `模块设计_齿条方案.STEP`。
当前包里保留了两类模型：

- STEP 导出的高精度 STL 网格，用于 RViz/Gazebo 外观预览。
- 面向 Gazebo 仿真的两自由度 URDF 模型，外观使用分组 STL，碰撞体使用简化几何。

简化碰撞体的目的是让 Gazebo 仿真更稳定、计算更轻；如果后续需要精细接触，再把局部碰撞体替换成更细的网格或凸包。

## 文件说明

- `model.config`：Gazebo Classic 模型元信息。
- `model.sdf`：可直接被 Gazebo Classic 加载的 SDF 模型。
- `urdf/xz_motion_mechanism.urdf`：两自由度 Gazebo/ros_control 动态模型，使用分组 STEP 网格作为视觉模型。
- `urdf/xz_motion_mechanism_preview.urdf`：早期 ROS/RViz 预览模型。
- `urdf/xz_motion_mechanism_step_visual.urdf`：使用完整 STEP 导出 STL 的 RViz 静态预览模型。
- `launch/gazebo_sim.launch`：启动 Gazebo 并生成两自由度模型，不加载控制器。
- `launch/gazebo_2dof.launch`：启动 Gazebo、生成两自由度模型，可通过参数选择是否加载控制器。
- `launch/display.launch`：ROS Noetic RViz 预览入口。
- `launch/display_step_visual.launch`：完整 STEP 外观的 RViz 静态预览入口。
- `launch/display_2dof.launch`：两自由度分组模型的 RViz 预览入口，可用滑条移动关节。
- `rviz/xz_motion_mechanism_preview.rviz`：早期 RViz 配置。
- `rviz/xz_motion_mechanism.rviz`：两自由度模型 RViz 配置。
- `rviz/xz_motion_mechanism_step_visual.rviz`：完整 STEP 外观 RViz 配置。
- `scripts/convert_step_with_freecad.py`：使用 FreeCAD 从 STEP 导出完整 STL 的辅助脚本。
- `scripts/export_grouped_step_meshes.py`：使用 FreeCAD 按部件名称分组导出 STL 的辅助脚本。
- `meshes/module_visual.stl`：从原始 STEP 导出的完整静态外观网格。
- `meshes/base_visual.stl`、`meshes/x_stage_visual.stl`、`meshes/y_stage_visual.stl`：两自由度模型使用的分组外观网格。
- `meshes/grouped_meshes_manifest.txt`：当前 STEP 零件到 `base/x_stage/y_stage` 的分组清单。

## Gazebo 中直接加载模型

从 `/home/hyf/Documents` 执行：

```bash
export GAZEBO_MODEL_PATH=/home/hyf/Documents/gazebo_rl_model
gazebo
```

然后在 Gazebo 的模型列表中插入 `xz_motion_mechanism_sim`，也可以通过 ROS 的 launch 文件生成模型。

## 启动两自由度 Gazebo 仿真

推荐先启动不带控制器的版本，确认模型姿态和外观正确：

```bash
cd /home/hyf/Documents
source /opt/ros/noetic/setup.bash
export ROS_PACKAGE_PATH=/home/hyf/Documents/gazebo_rl_model:$ROS_PACKAGE_PATH
roslaunch xz_motion_mechanism_sim gazebo_sim.launch
```

默认生成姿态会把 CAD 装配体立起来：

```text
spawn_z:=0.41
spawn_roll:=-1.57079632679
```

如果在你的 Gazebo 里方向正好反了，可以临时这样启动：

```bash
roslaunch xz_motion_mechanism_sim gazebo_2dof.launch spawn_roll:=1.57079632679
```

当前两自由度运动链为：

```text
world --fixed--> base_link --x_axis_joint--> x_stage_link --y_axis_joint--> y_stage_link
```

其中：

- `base_link`：固定底座、门架支架、横梁、固定导轨、横向长齿条和滚轮滑座。
- `x_stage_link`：相对横向长齿条运动的整套盒盖/滑座组件，包含顶部导轨滑块、电机、齿轮、执行机构连接件和盒盖等部件。
- `y_stage_link`：只有竖向齿条，作为相对盒盖组件运动的第二自由度部件。
- `x_axis_joint`：X 向直线关节，默认行程 `-0.50` 到 `0.50` m。
- `y_axis_joint`：Y 向直线关节，默认行程 `-0.24` 到 `0.24` m。

## 启动控制器

需要通过 topic 控制两个直线关节时，启动带控制器版本：

```bash
roslaunch xz_motion_mechanism_sim gazebo_2dof.launch controllers:=true
```

两个位置控制 topic 为：

```bash
/xz_motion_mechanism/x_axis_position_controller/command
/xz_motion_mechanism/y_axis_position_controller/command
```

示例命令：

```bash
rostopic pub -1 /xz_motion_mechanism/x_axis_position_controller/command std_msgs/Float64 "data: 0.25"
rostopic pub -1 /xz_motion_mechanism/y_axis_position_controller/command std_msgs/Float64 "data: 0.10"
```

也可以打开图形滑条控制面板：

```bash
roslaunch xz_motion_mechanism_sim joint_command_gui.launch
```

使用这个面板前，需要先用 `controllers:=true` 启动 Gazebo 模型。面板会以 20 Hz 持续发布两个关节的位置指令。

也可以一条命令同时启动 Gazebo、控制器和滑条面板：

```bash
roslaunch xz_motion_mechanism_sim sim_with_joint_gui.launch
```

## RViz 预览

RViz 需要 ROS 能找到这个包。先设置 `ROS_PACKAGE_PATH`：

```bash
cd /home/hyf/Documents
source /opt/ros/noetic/setup.bash
export ROS_PACKAGE_PATH=/home/hyf/Documents/gazebo_rl_model:$ROS_PACKAGE_PATH
```

预览完整 STEP 静态外观：

```bash
roslaunch xz_motion_mechanism_sim display_step_visual.launch
```

预览两自由度分组模型，并用滑条移动关节：

```bash
roslaunch xz_motion_mechanism_sim display_2dof.launch
```

如果缺少 `robot_state_publisher` 或 `joint_state_publisher`，需要安装对应的 ROS Noetic 软件包后再启动。

## 重新生成 STEP 外观网格

重新导出完整静态 STL：

```bash
cd /home/hyf/Documents/gazebo_rl_model/xz_motion_mechanism_sim/scripts
freecadcmd convert_step_with_freecad.py /home/hyf/Documents/model.STEP ../meshes/module_visual.stl
```

重新按部件分组导出两自由度 STL：

```bash
cd /home/hyf/Documents/gazebo_rl_model/xz_motion_mechanism_sim/scripts
freecadcmd export_grouped_step_meshes.py /home/hyf/Documents/model.STEP ../meshes
```

导出的 STL 单位是毫米。URDF/SDF 中使用 `scale="0.001 0.001 0.001"` 转成米，并用测得的 STEP 整体中心
`(347.488, 369.008, 590.000) mm` 做坐标居中。

## 建模假设

- 视觉模型来自 STEP 分组网格，尽量保持真实外观。
- 横向长齿条和 `滚轮滑座` 固定在 `base_link` 中，盒盖以下整套组件作为 `x_stage_link` 相对它们运动；竖向齿条作为 `y_stage_link` 再相对盒盖组件运动。
- 物理碰撞体是 box 简化模型，不追求齿条、齿轮、型材槽口等细节接触。
- 当前两自由度调试模型暂时关闭了碰撞体，避免粗略 box 和地面/运动部件穿插导致 Gazebo 发抖。
- 基座通过 `world_to_base` 固定在 Gazebo 世界中，防止机构作为自由刚体在重力下翻倒。
- 两个自由度用 Gazebo 支持良好的 prismatic joint 表达，适合先完成机构仿真和控制联调。
- 如果后续需要表达齿轮-齿条啮合，可以在控制层建立位移-转角映射，或者再增加 mimic/插件逻辑。
