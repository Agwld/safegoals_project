import board

# ==========================================
#        SAFEGOALS SEAT CONTROLLER
#           MASTER PIN MAP
# ==========================================

# --- HUB75 LED MATRIX (13 Pins) ---
MATRIX_R1 = board.GP0
MATRIX_G1 = board.GP1
MATRIX_B1 = board.GP2
MATRIX_R2 = board.GP3
MATRIX_G2 = board.GP4
MATRIX_B2 = board.GP5

MATRIX_ADDR_A = board.GP6
MATRIX_ADDR_B = board.GP7
MATRIX_ADDR_C = board.GP8
MATRIX_ADDR_D = board.GP9

MATRIX_CLK = board.GP10
MATRIX_LAT = board.GP11
MATRIX_OE  = board.GP12

# --- USER INPUTS (4 Pins) ---
BUTTON_1  = board.GP13
BUTTON_2  = board.GP14
BUTTON_3  = board.GP15
PANIC_BTN = board.GP22 

# --- RS485 COMMUNICATION (3 Pins) ---
RS485_TX  = board.GP16
RS485_RX  = board.GP17
RS485_DIR = board.GP18

# --- LIGHTING (2 Pins) ---
STRIP_MAIN  = board.GP19
STRIP_CHEER = board.GP27

# --- SENSORS (I2C) ---
I2C_SDA = board.GP20
I2C_SCL = board.GP21

# --- ANALOG MICROPHONE ---
MIC_INPUT = board.GP26

# --- SYSTEM INDICATOR ---
# Heartbeat LED
HEARTBEAT_LED = board.GP28