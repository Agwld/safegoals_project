#include "hub_buttons.h"


int main(){
	DDRA=0x00;
	PORTA=0x00;
	
	init_debug_uart0();
	uint8_t team;
	while(1){
		_delay_ms(100);
		if (PINA & _BV(PINA0)){
			start_emerg();
			while(1){
				printf("1");
				if(PINA & _BV(PINA4)){
					printf("\nstopped \n");
					break;
				}
			}
		}
		else if (PINA & _BV(PINA1)){//team A
			team = 1;
			start_goal(team);
		}
		else if (PINA & _BV(PINA2)){//team B
			team = 0;
			start_goal(team);
		}
		else if (PINA & _BV(PINA3)){
			start_tow();
			process_tow();
			printf("A: %d  B:  %d\n", tot_a_count, tot_b_count);
		}
	}
}