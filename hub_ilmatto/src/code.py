import board
import digitalio
import pwmio
import time

# ================= 硬件接口定义 (全右侧方案) =================
# 1. 播放开关 (接 GP22，物理引脚 29)
btn_play = digitalio.DigitalInOut(board.GP22)
btn_play.direction = digitalio.Direction.INPUT
btn_play.pull = digitalio.Pull.UP 

# 2. 功放开关 (接 GP26，物理引脚 31)
btn_amp = digitalio.DigitalInOut(board.GP26)
btn_amp.direction = digitalio.Direction.INPUT
btn_amp.pull = digitalio.Pull.UP

# 3. 功放启停控制 (接 GP27，物理引脚 32)
amp_shutdown = digitalio.DigitalInOut(board.GP27)
amp_shutdown.direction = digitalio.Direction.OUTPUT
amp_shutdown.value = False  # 初始设为 False (休眠)

# 4. 音频 PWM 输出 (接 GP28，物理引脚 34)
# 占空比设为 0 (静音)
speaker = pwmio.PWMOut(board.GP28, frequency=440, duty_cycle=0, variable_frequency=True)

# ================= (接下来的乐谱和主循环代码保持原样) =================

# ================= 乐谱与频率数据 =================
# 巴赫无伴奏大提琴组曲前奏曲片段
MELODY = """
X:1
T: Prelude from first Cello Suite
C: J.S. Bach, here transposed for mandolin
M: 4/4
L: 1/16
K:D
(DAf)e fAfA (DAf)e fAfA | (DBg)f gBgB (DBg)f gBgB |
(Dcg)f gcgc (Dcg)f gcgc | (Ddf)d fdfd (Ddf)d fdfd |
[D16Afd'] |]
"""

# 定义简易音阶频率字典 (等程音阶)
# 大写字母为低八度，小写字母为高八度
FREQUENCIES = {
    'C': 262, 'D': 294, 'E': 330, 'F': 349, 'G': 392, 'A': 440, 'B': 494,
    'c': 523, 'd': 587, 'e': 659, 'f': 698, 'g': 784, 'a': 880, 'b': 988
}

STEP_DELAY = 0.200 # 200毫秒 (原 C 代码的 STEP_DELAY_MS)

# ================= 核心逻辑 =================

def get_melody_generator():
    """这是一个 Python 生成器，用来按顺序吐出乐谱中的音符频率"""
    for char in MELODY:
        # 如果字符在我们的字典里，就吐出它的频率
        if char in FREQUENCIES:
            yield FREQUENCIES[char]
        # 如果是空格、括号、数字等其他字符，生成器会自动跳过，这比 C 语言的 M2F_UNKOWN 优雅得多！

# 初始化乐谱进度
current_melody = get_melody_generator()

print("八音盒已启动！等待按键...")

while True:
    # --- 逻辑 1：功放总控 ---
    if not btn_amp.value:      # 按钮按下 (接地，低电平)
        amp_shutdown.value = True  # 唤醒功放
    else:
        amp_shutdown.value = False # 功放休眠

    # --- 逻辑 2：歌曲播放控制 ---
    if not btn_play.value:     # 播放键按下
        try:
            # 尝试获取下一个音符频率
            freq = next(current_melody)
            
            # 设置频率并播放 (占空比 32768 意味着 50%，即最大音量的方波)
            speaker.frequency = freq
            speaker.duty_cycle = 32768
            time.sleep(STEP_DELAY)
            
            # 颗粒感断点 (原代码里的 10ms 静音)
            speaker.duty_cycle = 0
            time.sleep(0.01)
            
        except StopIteration:
            # 当生成器抛出 StopIteration，意味着整首歌读完了
            current_melody = get_melody_generator() # 重置回开头
            speaker.duty_cycle = 0                  # 静音
            time.sleep(1.0)                         # 停顿 1 秒
            
    else:
        # 播放键弹起：切断 PWM 信号，并把歌曲进度重置回开头
        speaker.duty_cycle = 0
        current_melody = get_melody_generator()
        time.sleep(0.05) # 消除按钮机械抖动的影响