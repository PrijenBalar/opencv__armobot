import time
from ArmControl import ArmControl

def sender_loop(command_queue):
    print("📡 Sender thread started")

    arm = ArmControl()

    while True:
        if not command_queue.empty():
            d_j1, d_j2, d_j3 = command_queue.get()

            try:
                pos = arm.get_current_position()
                if not pos:
                    continue

                if d_j1 != 0:
                    arm.move_joint(1, pos['joint1'] + d_j1)
                if d_j2 != 0:
                    arm.move_joint(2, pos['joint2'] + d_j2)
                if d_j3 != 0:
                    arm.move_joint(3, pos['joint3'] + d_j3)

                print("SENT →", d_j1, d_j2, d_j3)

            except Exception as e:
                print("❌ Sender error:", e)

        time.sleep(0.02)
