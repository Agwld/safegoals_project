import framebufferio
import rgbmatrix
import displayio
import pin_map

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
            clock_pin=pin_map.MATRIX_CLK,
            latch_pin=pin_map.MATRIX_LAT,
            output_enable_pin=pin_map.MATRIX_OE
        )
        self.display = framebufferio.FramebufferDisplay(matrix_pins)
        
        # Setup displayio groups/bitmaps
        self.group = displayio.Group()
        self.display.root_group = self.group

    def show_goal_animation(self):
        """Trigger a 'GOAL!' text scroll or animation."""
        pass

    def show_exit_arrow(self):
        """Show a high-contrast emergency exit arrow."""
        pass