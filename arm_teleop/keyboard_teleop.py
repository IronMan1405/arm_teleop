import rclpy 
from rclpy.node import Node

from geometry_msgs.msg import Vector3
from std_msgs.msg import Bool

import sys, termios, tty, threading

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop_keyboard')

        self.delta_pub = self.create_publisher(Vector3, '/arm/teleop_delta', 10)
        self.ori_pub = self.create_publisher(Bool, '/arm/orientation_constraint', 10)

        self.step = 0.02
        self.ori_constrained = False

        self.get_logger().info(
            "\nKeyboard teleop started\n"
            "[W/S]: +X/-X | [A/D]: +Y/-Y | [Q/E]: +Z/-Z\n"
            "[C]: enable/disable orientation constaint\n"
            "[H]: home | [ESC]: exit"
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
                # elif key == "h":
                    # go home
                
                elif key == 'c':
                    self.ori_constrained = not self.ori_constrained
                    msg = Bool()
                    msg.data = self.ori_constrained
                    self.ori_pub.publish(msg)
                    
                    state = "ENABLED" if self.ori_constrained else "DISABLED"
                    self.get_logger().info(f"Orientation constraint {state}")
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