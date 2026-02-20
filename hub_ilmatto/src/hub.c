#include "hub_buttons.h"
#include "gpio.h"
#include "comms.h"

Message store[MAX_SEATS] ={0};

Message* update_store(void){
	uint16_t i;
	for (i=0;i<MAX_SEATS;i++){
			store[i] = check_seat(i);
			update_displays_from_message(store[i],i);
	}
	return store;
}

int main(){
	DDRA=0x00;
	PORTA=0x00;
		
	init_debug_uart0();
	mcp23017_init();
	init_i2c_master();
	
	uint8_t team;
	while(1){
		//get seat data
		update_store();
		
		//hub commands
		if (PINA & _BV(PINA0)){//emergency signal on latch button
			start_emerg();
		}
		else if (PINA & _BV(PINA1)){//team A goal
			team = 1;
			start_goal(team);
		}
		else if (PINA & _BV(PINA2)){//team B goal
			team = 0;
			start_goal(team);
		}
		else if (PINA & _BV(PINA3)){//tug of war minigame
			start_tow();
			uint8_t timer = 100;
			while(timer > 0){
				update_store();//gain data from seat to process
				process_tow(store);
				timer--;
			}
		}
		else{//idle
			idle();
		}
	}
}