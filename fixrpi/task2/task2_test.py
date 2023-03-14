import serial 

ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/ttyUSB0'
# ser.port = '/dev/cu.usbserial-0002'
print(ser.open())
init = ['US025'] # move until 25cm before 1st obstacle
case_l = [
    # scan 1 = left
    'FL057', 'FR057', 'FW020',
    # move to 2nd obs
    'US230', # move until 30cm before 2nd obstacle
    'FR020',
]

case_r = [
    # scan 1 = right
    'FR057', 'FL057', 'FW020',
    # move to 2nd obs
    'US030', # move until 30cm before 2nd obstacle and save d to buff 0
    'FL020',
]

case_ll = [
    # scan 2 = left
    'BR020', 'FL067', 'FR067', 'FW030', 'FR090', 'FW067', 'FR090',
    'RT099', # d + 99
    'FR090', 'FW010', 'FL090',
    # back to base
    'US120' # move until 20cm before parking wall
]

case_lr = [
    # scan 2 = right
    'FR070', 'FW035', 'FL090', 'FW030', 'FL090', 'FW067', 'FL090', 
    'RT099', # d + 99
    'FL090', 'FW010', 'FR090',
    # back to base
    'US120' # move until 20cm before parking wall
]

case_rr = [
    # scan 2 = left
    'BL020', 'FR067', 'FL067', 'FW030', 'FL090', 'FW067', 'FL090',
    'RT099', # d + 99
    'FL090', 'FW010', 'FR090',
    # back to base
    'US120' # move until 20cm before parking wall
]

case_rl = [
    # scan 2 = right
    'FL070', 'FW035', 'FR090', 'FW030', 'FR090', 'FW067', 'FR090', 
    'RT099', # d + 99
    'FR090', 'FW010', 'FL090',
    # back to base
    'US120' # move until 20cm before parking wall
]

#instr_list = init + case_l + case_ll
instr_list = init + case_l + case_lr
#instr_list = init + case_r + case_rr
#instr_list = init + case_r + case_rl

for instr in instr_list:
    print(instr)
    ser.write(instr.encode())
    while True:
        raw_dat = ser.read(1)
        dat = raw_dat.strip().decode()
        print(raw_dat)
        if dat == 'R':
            break
print("done")