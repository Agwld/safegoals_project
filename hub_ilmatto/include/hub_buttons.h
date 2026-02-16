#include <avr/io.h>
#include "debug.h" //allows uart
#include <util/delay.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

uint16_t tot_a_count = 0;
uint16_t tot_b_count = 0;

void start_goal(uint8_t team){
	if (team){
		printf("a goal\n");
		_delay_ms(100);
	}
	else{
		printf("b goal\n");
		_delay_ms(100);
	}
}

void start_tow(){
	printf("tow\n");
}

void start_emerg(){
	printf("emergency\n");
}

void process_tow(){
	char buffer[16];
	uint8_t timer = 100;
	while(timer > 0){
		_delay_ms(100);
		fgets(buffer ,sizeof(buffer),stdin);
		
		if (strncmp(buffer, "A:", 2) == 0) {
			uint8_t a_count = (uint8_t)strtoul(buffer + 3, NULL, 10);
			tot_a_count += a_count;
		}
		else if (strncmp(buffer, "B:", 2) == 0) {
            uint8_t b_count = (uint8_t)strtoul(buffer + 2, NULL, 10);
			tot_b_count += b_count;
        }
		printf("%d",timer);
		timer--;
	}
}

void cheer_meter(){
	printf("cheer\n");
}
