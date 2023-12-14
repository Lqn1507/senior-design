from telnetlib import Telnet
import keyboard
import time
LINUXCNC = '10.0.0.2'
PORT = 5007
TIME_OUT = 3
tn = 0

login = False
enable = False
machine = False
estop = False
mode = False
vacuum=False
RUN   = False
ERROR = False
toggle = 0
Y_LIMIT = 800
X_LIMIT = 800
Z_LIMIT = 190

X_loc = 0
Y_loc = 0
Z_loc = 0
step=50


def location():
    if(login and enable and machine and mode and estop):
        #get current x position
        global X_loc,Y_loc,Z_loc
        tn.write(b"get abs_act_pos 0\n")
        tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
        pos = tn.read_until(b"\n", timeout=TIME_OUT)
        pos = pos.decode('utf-8')
        pos = pos[14:]
        pos = pos[:10]
        X_loc = float(pos)
        #get current y position
        tn.write(b"get abs_act_pos 1\n")
        tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
        pos = tn.read_until(b"\n", timeout=TIME_OUT)
        pos = pos.decode('utf-8')
        pos = pos[14:]
        pos = pos[:10]
        Y_loc = float(pos)
        #get current z position
        tn.write(b"get abs_act_pos 2\n")
        tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
        pos = tn.read_until(b"\n", timeout=TIME_OUT)
        pos = pos.decode('utf-8')
        pos = pos[14:]
        pos = pos[:10]
        Z_loc = float(pos)
        print('Current head position: {:6.2f}'.format(X_loc) + ' , {:6.2f}'.format(Y_loc) + ',  {:6.2f}'.format(Z_loc))
        
def up():
    y = Y_loc
    if(y+step<=Y_LIMIT):
        gcode = "set mdi g0y"+str(y+step)+"\n"
        tn.write(bytes(gcode, 'utf-8'))
        tn.read_until(b"\n", timeout=TIME_OUT)
        time.sleep(1)
        location()
    else:
        print("Cannot move")

def down():
    y = Y_loc
    if(Y_loc-step>=0):
        gcode = "set mdi g0y" + str(y-step) + "\n"
        tn.write(bytes(gcode, 'utf-8'))
        tn.read_until(b"\n", timeout=TIME_OUT)
        time.sleep(1)
        location()
    else:
        print("Cannot move")

def left():
    x = X_loc
    if(X_loc+step<=X_LIMIT):
        gcode = "set mdi g0x" + str(x-step)+ "\n"
        tn.write(bytes(gcode, 'utf-8'))
        tn.read_until(b"\n", timeout=TIME_OUT)
        time.sleep(1)
        location()
    else:
        print("Cannot move")

def right():
    x = X_loc
    if(X_loc-step>=0):
        gcode = "set mdi g0x" + str(x+step) + "\n"
        tn.write(bytes(gcode, 'utf-8'))
        tn.read_until(b"\n", timeout=TIME_OUT)
        time.sleep(1)
        location()
    else:
        print("Cannot move")


def manual():
    print("Ready for manual mode")
    keyboard.add_hotkey('Up', up) 
    keyboard.add_hotkey('Down', down) 
    keyboard.add_hotkey('Left', left) 
    keyboard.add_hotkey('Right', right) 

    
    keyboard.wait('esc')

def change_step():
    global step
    step = int(input("Input value of step"))

def rehome():
    gcode = "set mdi g0x0y0z0\n"
    tn.write(bytes(gcode, 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    time.sleep(4)

def home():
    tn.write(b"set mode manual\n")
    tn.read_until(b"\n", timeout=TIME_OUT)
    tn.write(b"set home -1\n")
    tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
    while(1):
        tn.write(b"get joint_homed\n")
        tn.read_until(b"\n", timeout=TIME_OUT) #read the command echo
        resp = tn.read_until(b"\n", timeout=TIME_OUT)
        if(resp==b"JOINT_HOMED YES YES YES NO NO NO\r\n"):
            print("ready to move")
            break
    tn.write(b"set mode mdi\n")
    tn.read_until(b"\n", timeout=TIME_OUT)

def pickup():
    gcode = "set mdi g0z185\n"
    tn.write(bytes(gcode, 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    time.sleep(5)
    tn.write(bytes('SET SPINDLE FORWARD\n', 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    vacuum=True
    time.sleep(5)
    gcode = "set mdi g0z" + str(0) + "\n"
    tn.write(bytes(gcode, 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    time.sleep(5)
    print("Pickup done")

def drop():
    gcode = "set mdi g0z" + str(180) + "\n"
    tn.write(bytes(gcode, 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    time.sleep(5)
    tn.write(bytes('SET SPINDLE OFF\n', 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    vacuum=False
    time.sleep(5)
    gcode = "set mdi g0z" + str(0) + "\n"
    tn.write(bytes(gcode, 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    time.sleep(5)
    print("Drop done")

def jogging(): 
    y=0
    for i in range (6):
        x=0
        for j in range(12):
            x=x+50
            gcode = "set mdi g0x" + str(x) + "\n"
            tn.write(bytes(gcode, 'utf-8'))
            tn.read_until(b"\n", timeout=TIME_OUT)
            time.sleep(2)
        y=y+50
        gcode = "set mdi g0y"+str(y)+"\n"
        tn.write(bytes(gcode, 'utf-8'))
        tn.read_until(b"\n", timeout=TIME_OUT)
        time.sleep(2)
        for j in range(12):
            x=x-50
            gcode = "set mdi g0x" + str(x) + "\n"
            tn.write(bytes(gcode, 'utf-8'))
            tn.read_until(b"\n", timeout=TIME_OUT)
            time.sleep(2)
        if(i!=5):
            y=y+50
            gcode = "set mdi g0y"+str(y)+"\n"
            tn.write(bytes(gcode, 'utf-8'))
            tn.read_until(b"\n", timeout=TIME_OUT)
            time.sleep(2)

def move(x,y):
    gcode = "set mdi g0x"+str(x)+"y"+str(y)+"\n"
    tn.write(bytes(gcode, 'utf-8'))
    tn.read_until(b"\n", timeout=TIME_OUT)
    time.sleep(2)

try:
    tn = Telnet(LINUXCNC, port=PORT, timeout=3)
except:
    print()
    # return False
# Login to remote shell
tn.write(b"hello EMC controller 1.0\n")
if(tn.read_until(b"\n", timeout=TIME_OUT)==b'HELLO ACK EMCNETSVR 1.1\r\n'):
    login = True
else:
    print('Error, failed to establish telnet connection')
# Enable LinuxCNC
tn.write(b"set enable EMCTOO\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
tn.write(b"get enable\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
if(tn.read_until(b"\n", timeout=TIME_OUT)==b'ENABLE ON\r\n'):
    enable = True
else:
    print('Error, failed to enable LinuxCNC')
# Disable estop
tn.write(b"set estop off\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
tn.write(b"get estop\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
if(tn.read_until(b"\n", timeout=TIME_OUT)==b'ESTOP OFF\r\n'):
    estop = True
else:
    print('Error, failed to turn off estop')
# Turn the machine on
tn.write(b"set machine on\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
tn.write(b"get machine\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
if(tn.read_until(b"\n", timeout=TIME_OUT)==b'MACHINE ON\r\n'):
    machine = True
    RUN = True
    toggle = 1
else:
    print('Error, failed to enable machine')
# Set mode mdi
tn.write(b"set mode mdi\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
tn.write(b"get mode\n")
tn.read_until(b"\n", timeout=TIME_OUT) #throw away the echo
if(tn.read_until(b"\n", timeout=TIME_OUT)==b'MODE MDI\r\n'):
    mode = True
else:
    print('Error, failed to set mode mdi')








if (login and enable and machine and mode and estop):
    home()
while(True):
    n=int(input("1 manual; 2 jogging; 3 move 4 set step 5 show location 6 home 7 pickup 8 drop 9 exit\n"))
    if(n==1):
        manual()
    elif(n==2):
        jogging()
    elif(n==3):
        x=input("x=")
        y=input("y=")
        move(x,y)
    elif(n==4):
        change_step()
    elif(n==5):
        location()
    elif(n==6):
        rehome()
    elif(n==7):
        pickup()
    elif(n==8):
        drop()
    elif(n==9):
        break
# change_step()
# manual()
# pickup()
# manual()
# drop()

# location()
# jogging()
# tn.write(b"set mdi g0x10y10z0\n")

