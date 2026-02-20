#include "debug.h"
#include <stdbool.h>

#define MAX_SEATS 2

typedef struct {
    uint8_t bit9;
    uint8_t bit8;
    uint8_t bits7_4;
    uint8_t bits3_0;
} Message;

bool receive_message(uint16_t *msg) {
    *msg = 0;

    for (int i = 0; i < 10; i++) {
        int byte = ugetchar0(stdin);

        if (byte == '\n' || byte == '\r') {
            // Message ended too early
            return false;
        }

        *msg |= (uint16_t)(byte & 0x1) << (9 - i);
    }

    // Consume the terminating newline
    int terminator = ugetchar0(stdin);
    if (terminator != '\n' && terminator != '\r') return false;

    return true;
}

Message parse_message(uint16_t msg) {
    Message m;
    m.bit9    = (msg >> 9) & 0x1; // occupancy bit
    m.bit8    = (msg >> 8) & 0x1; // assistance bit
    m.bits7_4 = (msg >> 4) & 0xF;
    m.bits3_0 = (msg >> 0) & 0xF;
    return m;
}

Message check_seat(uint8_t seat_number){
	uint16_t raw_msg = 0;
	uint8_t seat_code = seat_number + 16;
	
	printf("0x%02X\n",seat_code);
	while(!receive_message(&raw_msg));//wait for data
	
	Message parsed_msg = parse_message(raw_msg);
	return parsed_msg;
}
 
 
