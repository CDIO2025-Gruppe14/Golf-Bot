# How to run the EV3:

> **⚠️ Note:**  
> The 1. step is **not necessary** as the files should already be added to the EV3 device.

*How to add the files onto the Ev3:*
1. *scp -r "/path/to/your/local/Ev3motors" robot@<EV3_IP_ADDRESS>:~*  
    ○ *Replace "/path/to/your/local/Ev3motors" with the actual path to your Ev3motors folder on your computer.*  
    ○ *Replace <EV3_IP_ADDRESS> with the actual IP address of your EV3 device.*
2. Connect to the EV3 device via SSH:  
    ○ ssh robot@<EV3_IP_ADDRESS>
3. Enter password 'maker' when prompted
4. Navigate to project directory:  
    ○ cd Ev3motors
5. Now run in the Ev3:  
    ○ python3 ev3_socket_server.py
6. Afterwards run this locally on your computer (outside of the Ev3):  
    ○ python3 control_ev3_menu.py

## EV3 Device Login Credentials
1. Username: robot
2. Password: maker