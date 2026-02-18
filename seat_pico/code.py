import time
import digitalio
import pin_map
from matrix_display import MatrixDisplay
from network import RS485Network

print("Starting SAFEGOALS Seat Node...")

# Initialize the matrix display
matrix = MatrixDisplay()
if matrix:
    print("Matrix display initialized successfully.")
matrix.test()

# Initialise the network

net = RS485Network(baudrate = 9600)

# Initialize the heartbeat LED
heartbeat = digitalio.DigitalInOut(pin_map.HEARTBEAT_LED)
heartbeat.direction = digitalio.Direction.OUTPUT

print("System ready, Listening for hex commands...")

# We need a stopwatch variable for the heartbeat LED
last_heartbeat = time.monotonic()

while True:
    # ALWAYS CALL UPDATE: This makes the screen draw frame-by-frame!
    matrix.update()
    
    incoming_byte = net.update()
    
    if incoming_byte is not None:
        print(f"Received Command: {hex(incoming_byte)}")
        
        #Act on the command
        if incoming_byte == 0x01:
            matrix.show_goal_animation("A")
            
        elif incoming_byte == 0x02:
            matrix.show_goal_animation("B")
            
        elif incoming_byte == 0xEE:
            matrix.show_exit_arrow()
            
        elif incoming_byte == 0x00:
            matrix.test()
            
        else:
            print("Unknown byte is ignored.")
            
    
    # Blink the Heartbeat
    now = time.monotonic()
    if (now - last_heartbeat) >= 0.5:
        heartbeat.value = not heartbeat.value
        last_heartbeat = now
        
