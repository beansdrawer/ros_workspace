#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from my_interface.msg import MyPose
from datetime import datetime

class PoseTopicHandler(Node):
    def __init__(self):
        super().__init__('pose_subscriber')

        self.latest_pose = None

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.publisher = self.create_publisher(
            MyPose,
            '/my_pose',
            10
        )

        self.timer = self.create_timer(2.0, self.timer_callback)   # 2초마다 실행

    def pose_callback(self, msg: Pose):
        self.latest_pose = msg

    def timer_callback(self):
        if self.latest_pose is None:
            return

        msg = self.latest_pose
        print(f"x: {msg.x:.3f}, y: {msg.y:.3f}, theta: {msg.theta:.3f}")

        my_msg = MyPose()
        my_msg.x = msg.x
        my_msg.y = msg.y
        my_msg.theta = msg.theta
        my_msg.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.publisher.publish(my_msg)


def main(args=None):
    rclpy.init(args=args)
    node = PoseTopicHandler()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
