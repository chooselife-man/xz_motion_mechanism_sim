#!/usr/bin/env python3
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import rospy
from std_msgs.msg import Float64


class JointCommandGui:
    def __init__(self) -> None:
        rospy.init_node("xz_motion_mechanism_joint_command_gui", anonymous=True)

        self.x_min = rospy.get_param("~x_min", -0.50)
        self.x_max = rospy.get_param("~x_max", 0.50)
        self.y_min = rospy.get_param("~y_min", -0.24)
        self.y_max = rospy.get_param("~y_max", 0.24)
        self.rate_hz = rospy.get_param("~rate_hz", 20.0)

        x_topic = rospy.get_param(
            "~x_topic",
            "/xz_motion_mechanism/x_axis_position_controller/command",
        )
        y_topic = rospy.get_param(
            "~y_topic",
            "/xz_motion_mechanism/y_axis_position_controller/command",
        )

        self.x_pub = rospy.Publisher(x_topic, Float64, queue_size=1)
        self.y_pub = rospy.Publisher(y_topic, Float64, queue_size=1)
        self.x_topic = x_topic
        self.y_topic = y_topic

        self.root = tk.Tk()
        self.root.title("X-Z Motion Mechanism Joint Control")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.x_value = tk.DoubleVar(value=0.0)
        self.y_value = tk.DoubleVar(value=0.0)

        self._build_axis("X axis", self.x_value, self.x_min, self.x_max, 0)
        self._build_axis("Y axis", self.y_value, self.y_min, self.y_max, 1)

        button_frame = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        button_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
        ttk.Button(button_frame, text="Zero", command=self.zero).pack(side="left")
        ttk.Button(button_frame, text="Close", command=self.close).pack(side="right")

        self.status = tk.StringVar(value="Waiting for controller topics")
        ttk.Label(self.root, textvariable=self.status, padding=(12, 0, 12, 12)).grid(
            row=3,
            column=0,
            sticky="w",
        )

        self._publish_loop()
        self._status_loop()

    def _build_axis(
        self,
        label: str,
        variable: tk.DoubleVar,
        minimum: float,
        maximum: float,
        row: int,
    ) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=row, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text=label, width=8).grid(row=0, column=0, sticky="w")
        scale = ttk.Scale(
            frame,
            from_=minimum,
            to=maximum,
            variable=variable,
            orient="horizontal",
            length=360,
        )
        scale.grid(row=0, column=1, sticky="ew", padx=8)

        value_label = ttk.Label(frame, width=9)
        value_label.grid(row=0, column=2, sticky="e")

        def update_label(*_args) -> None:
            value_label.configure(text=f"{variable.get(): .3f} m")

        variable.trace_add("write", update_label)
        update_label()

    def _publish_loop(self) -> None:
        if rospy.is_shutdown():
            self.root.destroy()
            return
        self.x_pub.publish(Float64(self.x_value.get()))
        self.y_pub.publish(Float64(self.y_value.get()))
        delay_ms = max(10, int(1000.0 / self.rate_hz))
        self.root.after(delay_ms, self._publish_loop)

    def _status_loop(self) -> None:
        if rospy.is_shutdown():
            self.root.destroy()
            return
        x_connections = self.x_pub.get_num_connections()
        y_connections = self.y_pub.get_num_connections()
        if x_connections and y_connections:
            self.status.set("Connected to both joint controllers")
        else:
            self.status.set(
                f"Waiting: X subscribers={x_connections}, Y subscribers={y_connections}"
            )
        self.root.after(500, self._status_loop)

    def zero(self) -> None:
        self.x_value.set(0.0)
        self.y_value.set(0.0)

    def close(self) -> None:
        self.root.quit()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    JointCommandGui().run()
