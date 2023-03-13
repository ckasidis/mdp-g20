import serial 

ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/ttyUSB0'
# ser.port = '/dev/cu.usbserial-0002'
print(ser.open())
case_l = [
    # to 1st obs
    'US030', # d1 TODO: add sensor (move until 25cm before obstacle)
    # scan 1 = left
    'FL057', 'FR057', 'FW020',
    # move to 2nd obs
    'US033', # d2 TODO: add sensor (move until 25cm before obstacle)
    'FR020',
]

case_r = [
    # to 1st obs
    'US030', # d1 TODO: add sensor (move until 25cm before obstacle)
    # scan 1 = right
    'FR057', 'FL057', 'FW020',
    # move to 2nd obs
    'US033', # d2 TODO: add sensor (move until 25cm before obstacle)
    'FL020',
]

case_ll = [
    # scan 2 = left
    'BR020', 'FL067', 'FR067', 'FW013', 'FR090', 'FW067', 'FR090',
    'RT080', # d2 + 90 #TODO: save d2 in STM and add 90cm
    'FR090', 'FW010', 'FL090',
    # back to base
    'US120' # TODO: stop 15cm before wall
]

case_lr = [
    # scan 2 = right
    'FR070', 'FW030', 'FL090', 'FW013', 'FL090', 'FW067', 'FL090', 
    'RT080', # d2 + 90 #TODO: save d2 in STM and add 90cm
    'FL090', 'FW012', 'FR090',
    # back to base
    'US120' # TODO: stop 15cm before wall
]

case_rr = [
    # scan 2 = left
    'BL020', 'FR067', 'FL067', 'FW013', 'FL090', 'FW067', 'FL090',
    'RT080', # d2 + 90 #TODO: save d2 in STM and add 90cm
    'FL090', 'FW010', 'FR090',
    # back to base
    'US120' # TODO: stop 15cm before wall
]

case_rl = [
    # scan 2 = right
    'FL070', 'FW030', 'FR090', 'FW013', 'FR090', 'FW067', 'FR090', 
    'RT080', # d2 + 90 #TODO: save d2 in STM and add 90cm
    'FR090', 'FW012', 'FL090',
    # back to base
    'US120' # TODO: stop 15cm before wall
]

instr_list = case_l + case_ll
# instr_list = case_l + case_lr
# instr_list = case_r + case_rr
# instr_list = case_r + case_rl

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