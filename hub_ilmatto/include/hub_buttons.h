#include <avr/io.h>
#include "debug.h" //allows uart
#include <util/delay.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "comms.h"


uint16_t tot_a_count = 0;
uint16_t tot_b_count = 0;

void start_goal(uint8_t team){
	if (team){
		printf("0x01\n");
		_delay_ms(100);
	}
	else{
		printf("0x02\n");
		_delay_ms(100);
	}
}

void start_tow(){
	printf("0x03\n");
}

void start_emerg(){
	printf("0x04\n");
}

void process_tow(Message m[MAX_SEATS]){
	uint16_t i;
	tot_a_count = 0;
	tot_b_count = 0;
	for (i=0;i<MAX_SEATS;i++){
		uint8_t a_count = m[i].bits7_4;
		uint8_t b_count = m[i].bits3_0;
		
		tot_a_count = tot_a_count + a_count;
		tot_b_count = tot_b_count + b_count;
	}
	printf("A: %d  B:  %d\n", tot_a_count, tot_b_count);
}
void idle(){
	printf("0x00\n");
}

