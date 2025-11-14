# This code is created and tested by the Windows operating system.
import sys
import roslibpy
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
import pymysql
from datetime import datetime

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Communication with ROS")
        self.latest_pose = {'x': 0.0, 'y': 0.0, 'theta': 0.0}
        self.init_ui()
        self.init_ros()
        self.init_mysql()

    def init_ui(self):
        self.forward_btn = QPushButton("forward")
        self.backward_btn = QPushButton("backward")
        self.left_btn = QPushButton("left")
        self.right_btn = QPushButton("right")
        
        self.forward_btn.clicked.connect(self.forward_clicked)
        self.backward_btn.clicked.connect(self.backward_clicked)
        self.left_btn.clicked.connect(self.left_clicked)
        self.right_btn.clicked.connect(self.right_clicked)

        self.reset_btn = QPushButton("reset")
        self.savepose_btn = QPushButton("save pose")
        
        self.reset_btn.clicked.connect(self.reset_clicked)
        self.savepose_btn.clicked.connect(self.savepose_clicked)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.forward_btn, 0, 1)
        grid_layout.addWidget(self.left_btn, 1, 0)
        grid_layout.addWidget(self.backward_btn, 1, 1)
        grid_layout.addWidget(self.right_btn, 1, 2)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.reset_btn)
        bottom_layout.addWidget(self.savepose_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def init_ros(self):
        self.client = roslibpy.Ros(host='localhost', port=9090)
        self.client.run()

        self.pose_topic = roslibpy.Topic(
            self.client,
            '/my_pose',
            'my_interface/msg/MyPose'
        )
        self.pose_topic.subscribe(self.pose_callback)

        self.cmd_vel_pub = roslibpy.Topic(
            self.client,
            '/turtle1/cmd_vel',
            'geometry_msgs/msg/Twist'
        )

        self.reset_service = roslibpy.Service(
            self.client,
            '/reset',
            'turtlesim/srv/Reset'
        )


    def init_mysql(self):
        self.db = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            database='rosdb',
            charset='utf8'
        )
        self.cursor = self.db.cursor()

    def pose_callback(self, message):
        self.latest_pose['x'] = message.get('x', 0.0)
        self.latest_pose['y'] = message.get('y', 0.0)
        self.latest_pose['theta'] = message.get('theta', 0.0)
        print("Received:", self.latest_pose)

    def closeEvent(self, event):
        if hasattr(self, 'pose_topic'):
            self.pose_topic.unsubscribe()
        if hasattr(self, 'client'):
            self.client.terminate()
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'db'):
            self.db.close()
        super().closeEvent(event)

    def forward_clicked(self):
        self.cmd_vel_pub.publish({
            'linear': {'x': 1.0, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
        })
        print("Forward")

    def backward_clicked(self):
        self.cmd_vel_pub.publish({
            'linear': {'x': -1.0, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
        })
        print("Backward")

    def left_clicked(self):
        self.cmd_vel_pub.publish({
            'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': 1.0}
        })
        print("Turn Left")

    def right_clicked(self):
        self.cmd_vel_pub.publish({
            'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': -1.0}
        })
        print("Turn Right")

    def reset_clicked(self):
        req = roslibpy.ServiceRequest({})
        self.reset_service.call(req)
        print("Reset service called")


    def savepose_clicked(self):
        x = self.latest_pose['x']
        y = self.latest_pose['y']
        theta = self.latest_pose['theta']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO turtlepos (x, y, theta, time) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql, (x, y, theta, now))
        self.db.commit()
        print("Saved pose:", x, y, theta, now)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
