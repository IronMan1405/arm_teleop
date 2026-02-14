import rclpy 
from rclpy.node import Node

from geometry_msgs.msg import Vector3
from std_msgs.msg import Bool, String

import sys, termios, tty, threading

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop_keyboard')

        self.delta_pub = self.create_publisher(Vector3, '/arm/teleop_delta', 10)
        self.ori_pub = self.create_publisher(Bool, '/arm/orientation_constraint', 10)
        self.named_pose_pub = self.create_publisher(String, '/arm/named_pose', 10)
        self.emergency_req_pub = self.create_publisher(Bool, '/arm/emergency_stop_request', 10)

        self.step = 0.05
        self.ori_constrained = False
        self.pending_delta = Vector3()
        self.req_emergency = False


        self.get_logger().info(
            "\nKeyboard teleop started\n"
            "[W/S]: +X/-X | [A/D]: +Y/-Y | [Q/E]: +Z/-Z\n"
            "[C]: enable/disable orientation constaint\n"
            "[O]: Zero Pose | [H]: home | [ESC]: exit"
        )

        self._stop = False
        self.thread = threading.Thread(target=self.keyboard_loop, daemon=True)
        self.thread.start()

    def keyboard_loop(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)

            while not self._stop:
                key = sys.stdin.read(1)

                delta = Vector3()

                if key == "w":
                    delta.x = self.step
                elif key == "s":
                    delta.x = -self.step
                elif key == "a":
                    delta.y = self.step
                elif key == "d":
                    delta.y = -self.step
                elif key == "q":
                    delta.z = self.step
                elif key == "e":
                    delta.z = -self.step

                elif key == "h":
                    msg = String()
                    msg.data = 'home'
                    self.named_pose_pub.publish(msg)
                    self.get_logger().info("Sent HOME pose")
                    continue
                elif key == 'o':
                    msg = String()
                    msg.data = 'zero'
                    self.named_pose_pub.publish(msg)
                    self.get_logger().info("Sent ZERO pose")
                    continue

                elif key == 'f':
                    msg = String()
                    msg.data = 'front'
                    self.named_pose_pub.publish(msg)
                    self.get_logger().info("Sent FRONT pose")
                    continue

                elif key == 'b':
                    msg = String()
                    msg.data = 'back'
                    self.named_pose_pub.publish(msg)
                    self.get_logger().info("Sent BACK pose")
                    continue
                
                elif key == 'c':
                    self.ori_constrained = not self.ori_constrained
                    msg = Bool()
                    msg.data = self.ori_constrained
                    self.ori_pub.publish(msg)
                    
                    state = "ENABLED" if self.ori_constrained else "DISABLED"
                    self.get_logger().info(f"Orientation constraint {state}")
                    continue

                elif key == " ":
                    self.req_emergency = not self.req_emergency
                    msg = Bool()
                    msg.data = self.req_emergency
                    self.emergency_req_pub.publish(msg)

                    state = "ENABLED" if self.req_emergency else "DISABLED"
                    self.get_logger().info(f"Emergency STOP {state}")
                    continue

                elif key == '\x1b':
                    self.get_logger().info("exiting teleop")
                    self._stop = True
                    rclpy.shutdown()
                    break

                else:
                    continue

                self.delta_pub.publish(delta)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():
    rclpy.init()
    node = KeyboardTeleop()
    rclpy.spin(node)

if __name__ == "__main__":
    main()