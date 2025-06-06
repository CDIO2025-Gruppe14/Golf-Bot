from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank
from time import sleep

tank = MoveTank(OUTPUT_A, OUTPUT_B)
tank.on_for_seconds(SpeedPercent(50), SpeedPercent(50), 2)