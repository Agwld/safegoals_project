import busio
import pin_map

class RS485Network:
    def __init__(self, baudrate=9600):
        """Initializes the RS485 UART connection for raw byte transfers."""
        self.uart = busio.UART(
            tx=pin_map.RS485_TX,
            rx=pin_map.RS485_RX,
            baudrate=baudrate,
            rs485_dir=pin_map.RS485_DIR,
            timeout=0 
        )
        
        # A queue to hold incoming bytes in case several arrive at once
        self.buffer = bytearray()

    def send(self, command_byte):
        """Sends a single raw byte over the RS485 bus."""
        # Convert the integer (e.g., 0x01) into a 1-byte payload and send it
        self.uart.write(bytes([command_byte]))

    def update(self):
        """
        Reads incoming data. Returns the oldest byte in the queue as an integer 
        (e.g., 0x01), or None if no bytes have been received.
        """
        # 1. Pull any new bytes from the hardware into our buffer
        if self.uart.in_waiting > 0:
            raw_data = self.uart.read(self.uart.in_waiting)
            if raw_data:
                self.buffer.extend(raw_data)
                
        # 2. If we have bytes in the buffer, pop the first one off and return it
        if len(self.buffer) > 0:
            command = self.buffer[0]
            self.buffer = self.buffer[1:] # Remove the byte we just read
            return command
            
        return None