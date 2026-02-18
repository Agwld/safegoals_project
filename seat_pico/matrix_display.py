import framebufferio
import rgbmatrix
import displayio
import pin_map
import terminalio
import random
import time
from adafruit_display_text import label

class MatrixDisplay:
    def __init__(self):
        # Release any existing displays to avoid 'Resource in use'
        displayio.release_displays()

        # HUB75 Configuration for a 64x32 matrix
        matrix_pins = rgbmatrix.RGBMatrix(
            width=64, bit_depth=4,
            rgb_pins=[pin_map.MATRIX_R1, pin_map.MATRIX_G1, pin_map.MATRIX_B1, 
                      pin_map.MATRIX_R2, pin_map.MATRIX_G2, pin_map.MATRIX_B2],
            addr_pins=[pin_map.MATRIX_ADDR_A, pin_map.MATRIX_ADDR_B, 
                       pin_map.MATRIX_ADDR_C, pin_map.MATRIX_ADDR_D],
            clock_pin=pin_map.MATRIX_CLK, latch_pin=pin_map.MATRIX_LAT,
            output_enable_pin=pin_map.MATRIX_OE
        )
        self.display = framebufferio.FramebufferDisplay(matrix_pins)

        # Setup displayio groups
        self.group = displayio.Group()
        self.display.root_group = self.group

        # --- STATE MACHINE VARIABLES ---
        self.state = "IDLE"            # Tracks what animation is currently running
        self.last_update = 0           # Stopwatch for timing frames
        self.frame_count = 0           # Tracks how many frames have played
        self.wipe_c = 0                # Tracks the diagonal wipe progress
        
        # Pointers to graphics so we can modify them later
        self.wipe_bitmap = None 
        self.wipe_grid = None
        self.fw_bitmap = None
        self.arrow_grid = None
        self.particles = []

    def clear(self):
        while len(self.group) > 0:
            self.group.pop()

    def test(self):
        """Run a simple test pattern to verify the display is working."""
        self.clear()
        bitmap = displayio.Bitmap(64, 32, 2)
        palette = displayio.Palette(2)
        palette[0] = 0x000000
        palette[1] = 0x222222
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        self.group.append(tile_grid)
        
        for x in range(64):
            for y in range(32):
                bitmap[x, y] = (x + y) % 2
                
        title_grid = displayio.TileGrid(displayio.Bitmap(64, 8, 2), pixel_shader=palette)
        self.group.append(title_grid)
        
        title_text = label.Label(terminalio.FONT, text="SAFEGOALS", color=0xfcba03)
        title_text.x = 0
        title_text.y = 4
        self.group.append(title_text)
        
        self.state = "IDLE" # Ensure we aren't trying to animate the test pattern

    # ==========================================
    #             ANIMATION TRIGGERS
    # ==========================================
    def show_goal_animation(self, team):
        """Sets up the graphics and kicks off the animation state machine."""
        self.clear()
        
        # 1. SETUP TEXT
        goal_text = label.Label(terminalio.FONT, text="GOAL!", color=0xFFD700, scale=2)
        goal_text.x = 5
        goal_text.y = 10 
        
        team_text = None
        if team == "A":
            team_text = label.Label(terminalio.FONT, text="TEAM A", color=0xFFD700)
            team_text.x = 13
            team_text.y = 25 
        elif team == "B":
            team_text = label.Label(terminalio.FONT, text="TEAM B", color=0xFFD700)
            team_text.x = 13
            team_text.y = 25 
        
        # 2. SETUP CURTAIN
        self.wipe_bitmap = displayio.Bitmap(64, 32, 8) 
        wipe_palette = displayio.Palette(8)
        wipe_palette.make_transparent(0)
        wipe_palette[1] = 0x000000
        wipe_palette[2] = 0xFF0000 
        wipe_palette[3] = 0xFF7F00 
        wipe_palette[4] = 0xFFFF00 
        wipe_palette[5] = 0x00FF00 
        wipe_palette[6] = 0x0000FF 
        wipe_palette[7] = 0x8B00FF 
        
        for x in range(64):
            for y in range(32):
                self.wipe_bitmap[x, y] = 1
                
        self.wipe_grid = displayio.TileGrid(self.wipe_bitmap, pixel_shader=wipe_palette)
        
        # 3. ADD TO GROUP
        self.group.append(goal_text)
        if team_text:
            self.group.append(team_text)
        self.group.append(self.wipe_grid)

        # 4. KICKSTART THE STATE MACHINE
        self.state = "WIPE_FILL"
        self.wipe_c = 0
        self.last_update = time.monotonic() # Start the stopwatch

    def show_exit_arrow(self):
        """Show a high-contrast emergency exit arrow."""
        self.clear()
        # Warning Text
        top_text = label.Label(terminalio.FONT, text="EMERGENCY", color=0xFF0000)
        top_text.x = 5
        top_text.y = 4
        
        bottom_text = label.Label(terminalio.FONT, text="EXIT NOW", color=0xFF0000)
        bottom_text.x = 8
        bottom_text.y = 28
        
        # Make the bitmap 96 pixels wide (wider than the 64px screen)
        # to hide the edges during the scrolling illusion
        arrow_bitmap = displayio.Bitmap(96, 14, 2)
        arrow_palette = displayio.Palette(2)
        arrow_palette.make_transparent(0)
        arrow_palette[1] = 0xFF0000 # Bright Red
        
        # Draw 4 chevrons, spaced exactly 24 pixels apart
        for cx in range(0, 96, 24):
            for dy in range(14):
                # Math to create a '<' shape pointing left
                vx = abs(dy - 6) 
                
                # Make the chevron line 4 pixels thick
                for thickness in range(4):
                    px = cx + vx + thickness
                    if 0 <= px < 96:
                        arrow_bitmap[px, dy] = 1

        self.arrow_grid = displayio.TileGrid(arrow_bitmap, pixel_shader=arrow_palette)
        self.arrow_grid.y = 9 # Float it perfectly between the two text labels
        
        # Add to group
        self.group.append(top_text)
        self.group.append(bottom_text)
        self.group.append(self.arrow_grid)

        # Start State Machine
        self.state = "EXIT_ARROW"
        self.last_update = time.monotonic()

    # ==========================================
    #             THE ENGINE (UPDATE)
    # ==========================================
    def update(self):
        """Must be called continuously in the main code.py loop."""
        if self.state == "IDLE":
            return

        now = time.monotonic()

        # --- PHASE 1: FILL WITH RAINBOW ---
        if self.state == "WIPE_FILL":
            # We process 4 steps of the wipe at a time to keep it fast
            for _ in range(4):
                if self.wipe_c >= 96:
                    self.state = "WIPE_PAUSE"
                    self.last_update = now # Reset stopwatch for the pause
                    break
                
                for x in range(64):
                    y1 = self.wipe_c - x
                    y2 = (self.wipe_c + 1) - x
                    if 0 <= y1 < 32:
                        self.wipe_bitmap[x, y1] = (self.wipe_c % 6) + 2
                    if 0 <= y2 < 32:
                        self.wipe_bitmap[x, y2] = ((self.wipe_c + 1) % 6) + 2
                self.wipe_c += 2

        # --- PHASE 2: PAUSE ON FULL COLOR ---
        elif self.state == "WIPE_PAUSE":
            if now - self.last_update >= 0.1: # Wait 0.1 seconds
                self.state = "WIPE_ERASE"
                self.wipe_c = 0

        # --- PHASE 3: ERASE THE CURTAIN ---
        elif self.state == "WIPE_ERASE":
            for _ in range(4):
                if self.wipe_c >= 96:
                    # Remove the curtain and prep the fireworks
                    self.group.remove(self.wipe_grid)
                    self._setup_fireworks()
                    self.state = "FIREWORKS"
                    self.frame_count = 0
                    self.last_update = now
                    break
                
                for x in range(64):
                    y1 = self.wipe_c - x
                    y2 = (self.wipe_c + 1) - x
                    if 0 <= y1 < 32:
                        self.wipe_bitmap[x, y1] = 0
                    if 0 <= y2 < 32:
                        self.wipe_bitmap[x, y2] = 0
                self.wipe_c += 2

        # --- PHASE 4: FIREWORKS ---
        elif self.state == "FIREWORKS":
            # Only draw a frame every 0.05 seconds
            if now - self.last_update >= 0.05:
                self._draw_fireworks_frame()
                self.last_update = now
                self.frame_count += 1
                
                if self.frame_count >= 160:
                    self.test()
                    self.state = "IDLE" # Animation is fully complete!
                
        # --- PHASE 5: EMERGENCY EXIT ARROW ---
        elif self.state == "EXIT_ARROW":
            # Move the arrows left every 0.02 seconds for a fast, urgent scroll
            if now - self.last_update >= 0.02:
                self.arrow_grid.x -= 1
                
                # THE ILLUSION: If we've scrolled left by exactly one chevron's 
                # spacing (24px), snap it seamlessly back to 0. 
                if self.arrow_grid.x <= -24:
                    self.arrow_grid.x += 24
                    
                self.last_update = now
        

    # ==========================================
    #             HELPER METHODS
    # ==========================================
    def _setup_fireworks(self):
        self.fw_bitmap = displayio.Bitmap(64, 32, 6)
        fw_palette = displayio.Palette(6)
        fw_palette.make_transparent(0) 
        fw_palette[1] = 0xFF0000 
        fw_palette[2] = 0x00FF00 
        fw_palette[3] = 0x0000FF 
        fw_palette[4] = 0xFFFFFF 
        fw_palette[5] = 0xFF00FF 
        
        fw_grid = displayio.TileGrid(self.fw_bitmap, pixel_shader=fw_palette)
        self.group.append(fw_grid)
        self.particles = []

    def _draw_fireworks_frame(self):
        if random.random() < 0.1:
            color = random.randint(1, 5)
            start_x = random.randint(10, 54)
            start_y = random.randint(5, 20) 
            for _ in range(random.randint(15, 20)):
                dx = (random.random() - 0.5) * 4 
                dy = (random.random() - 0.5) * 4
                self.particles.append([start_x, start_y, dx, dy, color, 0])

        alive_particles = []
        for p in self.particles:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < 64 and 0 <= y < 32:
                self.fw_bitmap[x, y] = 0 
            
            p[0] += p[2] 
            p[1] += p[3] 
            p[3] += 0.2  
            p[5] += 1    
            
            if p[5] < 12:
                new_x, new_y = int(p[0]), int(p[1])
                if 0 <= new_x < 64 and 0 <= new_y < 32:
                    self.fw_bitmap[new_x, new_y] = p[4]
                alive_particles.append(p)
        
        self.particles = alive_particles