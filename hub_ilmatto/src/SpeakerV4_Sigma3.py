import board
import pwmio
import digitalio
import time

# --- Hardware Interface ---
# GP22 (Pin 29) -> Play Switch
btn_play = digitalio.DigitalInOut(board.GP22)
btn_play.direction = digitalio.Direction.INPUT
btn_play.pull = digitalio.Pull.UP 

# GP26 (Pin 31) -> Amp Master Switch
btn_amp = digitalio.DigitalInOut(board.GP26)
btn_amp.direction = digitalio.Direction.INPUT
btn_amp.pull = digitalio.Pull.UP

# GP27 (Pin 32) -> PAM8302 SD Pin
amp_shutdown = digitalio.DigitalInOut(board.GP27)
amp_shutdown.direction = digitalio.Direction.OUTPUT
amp_shutdown.value = False  

# GP28 (Pin 34) -> Audio Out
speaker = pwmio.PWMOut(board.GP28, frequency=440, duty_cycle=0, variable_frequency=True)

# --- Audio Generator ---
def get_panic_generator():
    pattern = [
        (392, 0.30), (0, 0.05), (392, 0.30), (0, 0.15),
        (466, 0.15), (0, 0.05), (523, 0.15), (0, 0.15),
        (392, 0.30), (0, 0.05), (392, 0.30), (0, 0.15),
        (349, 0.15), (0, 0.05), (370, 0.15), (0, 0.15)
    ]
    while True:
        for freq, duration in pattern:
            yield freq, duration

current_alarm = get_panic_generator()
print("--- Stadium Security System Online ---")

# --- Logic Loop ---
while True:
    # 1. Check Amp Switch
    if not btn_amp.value:
        if amp_shutdown.value == False:
            print("Action: Amplifier AWAKE")
        amp_shutdown.value = True  
    else:
        if amp_shutdown.value == True:
            print("Action: Amplifier SLEEP")
        amp_shutdown.value = False 

    # 2. Check Play Switch
    if not btn_play.value:
        # Check if Amp is actually on before playing
        if amp_shutdown.value == True:
            freq, duration = next(current_alarm)
            if freq > 0:
                speaker.frequency = freq
                speaker.duty_cycle = 32768  
            else:
                speaker.duty_cycle = 0      
            time.sleep(duration)
        else:
            # If Play is pressed but Amp is off, do nothing but alert user
            print("Notice: Play pressed but AMP is OFF")
            time.sleep(0.2)
    else:
        # Reset if play button is released
        if speaker.duty_cycle != 0:
            print("Action: Stop and Reset")
        speaker.duty_cycle = 0
        current_alarm = get_panic_generator()
        time.sleep(0.05)