#include <stdint.h>
#include "i2c.h" //same as c7 lab (configure il matto to master mode)
#include "comms.h"


// MCP23017 I2C address (A0=A1=A2=0)
#define MCP23017_ADDR   0x20

// MCP23017 Register addresses
#define IODIRA          0x00    // Port A direction register
#define IODIRB          0x01    // Port B direction register
#define GPIOA           0x12    // Port A data register
#define GPIOB           0x13    // Port B data register

//Digit Select
#define DIGIT_1 0x01
#define DIGIT_2 0x02
#define DIGIT_3 0x04
#define DIGIT_4 0x08

#define BLANK 0x00
#define DASH 0x40

uint8_t display_buffer[4];

// Segment encoding for common cathode (active HIGH)
// Bit order: bit6=G, bit5=F, bit4=E, bit3=D, bit2=C, bit1=B, bit0=A
const uint8_t SEGMENT_MAP[10] = {
    0x3F,  // 0 -> 0b00111111
    0x06,  // 1 -> 0b00000110
    0x5B,  // 2 -> 0b01011011
    0x4F,  // 3 -> 0b01001111
    0x66,  // 4 -> 0b01100110
    0x6D,  // 5 -> 0b01101101
    0x7D,  // 6 -> 0b01111101
    0x07,  // 7 -> 0b00000111
    0x7F,  // 8 -> 0b01111111
    0x6F,  // 9 -> 0b01101111
};

void i2c_write_register(uint8_t i2c_addr, uint8_t reg, uint8_t data)
{
    i2c_start();
    i2c_tx((i2c_addr << 1) | 0x00);  // address + write bit
    i2c_tx(reg);                     // register to write
    i2c_tx(data);                    // value to write
    i2c_stop();
}

void mcp23017_init() {
    // Set both ports as outputs
    i2c_write_register(MCP23017_ADDR, IODIRA, 0x00);
    i2c_write_register(MCP23017_ADDR, IODIRB, 0x00);

    // Clear both displays on startup
    i2c_write_register(MCP23017_ADDR, GPIOA, 0x00);
    i2c_write_register(MCP23017_ADDR, GPIOB, 0x00);
}

void set_display(uint8_t digit1, uint8_t digit2, uint8_t digit3, uint8_t digit4){
    display_buffer[0] = SEGMENT_MAP[digit1 % 10];
    display_buffer[1] = SEGMENT_MAP[digit2 % 10];
    display_buffer[2] = SEGMENT_MAP[digit3 % 10];
    display_buffer[3] = SEGMENT_MAP[digit4 % 10];
}

const uint8_t digit_select[4] = {DIGIT_1, DIGIT_2, DIGIT_3, DIGIT_4};

void mux_7seg(void)
{
    static uint8_t active = 0;
    // Blank all digits first to prevent ghosting
    i2c_write_register(MCP23017_ADDR, GPIOB, 0x00);

    // Write segment pattern for active 7seg
    i2c_write_register(MCP23017_ADDR, GPIOA, display_buffer[active]);

    // Write on 7seg
    i2c_write_register(MCP23017_ADDR, GPIOB, digit_select[active]);

    // Next 7seg
    active = (active + 1) % 4;
}

void set_occupied(uint8_t count){		
    if (count > 99) count = 99;
    display_buffer[0] = (count >= 10) ? SEGMENT_MAP[count / 10] : BLANK;
    display_buffer[1] = SEGMENT_MAP[count % 10];
}

void set_assistance(uint8_t seat){
    if (seat > 99) seat = 99;
    display_buffer[2] = (seat >= 10) ? SEGMENT_MAP[seat / 10] : BLANK;
    display_buffer[3] = SEGMENT_MAP[seat % 10];
}

void clear_assistance(void){
    display_buffer[2] = DASH;
    display_buffer[3] = DASH;
}

void update_displays_from_message(Message msg, uint8_t seat_number) {
	
	// Update seat occupancy
    static uint8_t occupied_count = 0;
    static uint8_t prev_occupied[MAX_SEATS] = {0};

    if (msg.bit9 && !prev_occupied[seat_number]) {
        if (occupied_count < 99) occupied_count++;
    } else if (!msg.bit9 && prev_occupied[seat_number]) {
        if (occupied_count > 0) occupied_count--;
    }
    prev_occupied[seat_number] = msg.bit9;
    set_occupied(occupied_count);
    
    // Handle assistance request
    if (msg.bit8) {
        // Assistance requested
        set_assistance(seat_number);
    } else {
        // Clear assistance display
        clear_assistance();
    }
}