'''
  board_test.py - This is basic Finamon GNSS/Modem BG770A Shield HW using example.
'''

import board_hw
import time

shield = board_hw.board_hw()

print("user LED ON") 
shield.turnOnUserLED()
time.sleep(2)

print("user LED OFF") 
shield.turnOffUserLED()


