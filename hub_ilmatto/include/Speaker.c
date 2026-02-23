/*
 * Game Console - Audio Amplifier Dual-Switch Test
 * * Hardware Interface / Pin Assignments:
 * - SPEAKER_PWM : PD5 (PORT D, Pin 6) - 4000Hz PWM output
 * - SHUTDOWN    : PD4 (PORT D, Pin 5) - Amplifier SD control (High = Active, Low = Shutdown)
 * - SW_PWM      : PA0 (PORT A, Pin 1) - PWM output enable switch (Active Low)
 * - SW_SD       : PA1 (PORT A, Pin 2) - Amplifier wake-up switch (Active Low)
 */

#include <avr/io.h>

#define FREQ 4000          // Buzzer frequency: 4000Hz
#define TONE_PRESCALER 8UL // Timer1 prescaler
#define F_CPU 12000000     // Il Matto clock frequency: 12MHz

// Switch pin definitions on PORT A
#define SW_PWM PA0
#define SW_SD  PA1

void init_tone(void);
void tone(uint16_t frequency);

int main(void) {
    // 1. Initialize Timer1 (OC1A) to generate 4000Hz square wave in the background
    init_tone();
    tone(FREQ);

    // 2. Configure SHUTDOWN pin (PD4)
    DDRD |= _BV(PD4);    // Set PD4 as output
    PORTD &= ~_BV(PD4);  // Default to low (Amplifier in Shutdown/Mute state)

    // 3. Configure test switch pins on PORT A
    DDRA &= ~(_BV(SW_PWM) | _BV(SW_SD)); // Set as input
    PORTA |= (_BV(SW_PWM) | _BV(SW_SD)); // Enable internal pull-up resistors

    // 4. Main loop: poll switch states independently
    for (;;) {
        
        // --- Logic 1: Control PWM output on PD5 ---
        if (bit_is_clear(PINA, SW_PWM)) {
            // Switch grounded (pressed): Set PD5 as output to allow PWM signal
            DDRD |= _BV(PD5);  
        } else {
            // Switch open (released): Disconnect PD5 output and pull low
            DDRD &= ~_BV(PD5); 
            PORTD &= ~_BV(PD5); 
        }

        // --- Logic 2: Control Amplifier SHUTDOWN on PD4 ---
        if (bit_is_clear(PINA, SW_SD)) {
            // Switch grounded (pressed): Output High to wake up PAM8302
            PORTD |= _BV(PD4);  
        } else {
            // Switch open (released): Output Low to enter Shutdown mode
            PORTD &= ~_BV(PD4); 
        }
    }
}

/* Initialize Timer1 for square wave generation (Linked to PD5/OC1A) */
void init_tone(void) {
    TCCR1A = _BV(COM1A0) | _BV(WGM10);
    TCCR1B = _BV(WGM13) | _BV(CS11);
}

/* Set square wave frequency */
void tone(uint16_t frequency) {
    OCR1A = (uint16_t)(F_CPU / (2 * 2 * TONE_PRESCALER) / frequency);
}
