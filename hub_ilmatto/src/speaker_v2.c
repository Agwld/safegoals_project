#include <stdlib.h>
#include <avr/io.h>
#include <util/delay.h>
#include "et_scale.h"

#define TONE_PRESCALER 8UL
#define F_CPU 12000000

/* Port map (English) */
/* PD5 (OC1A): speaker PWM audio output */
/* PD4       : amplifier shutdown control (SHUTDOWN) */
/* PA0       : play switch input, active-low with pull-up (SW_PLAY) */
/* PA1       : amplifier switch input, active-low with pull-up (SW_AMP) */
#define SW_PLAY PA0
#define SW_AMP  PA1

#define STEP_DELAY_MS 200

#define M2F_END    0
#define M2F_REST   1
#define M2F_UNKOWN 2

const char melody[] ="\\
X:1\n\\
T: Prelude from first Cello Suite\n\\
C: J.S. Bach, here transposed for mandolin\n\\
M: 4/4\n\\
L: 1/16\n\\
K:D\n\\
(DAf)e fAfA (DAf)e fAfA | (DBg)f gBgB (DBg)f gBgB |\n\\
(Dcg)f gcgc (Dcg)f gcgc | (Ddf)d fdfd (Ddf)d fdfd |\n\\
[D16Afd'] |]\\
";

void init_tone(void);
void tone(uint16_t frequency);
uint16_t melody2freq(const char *abc_melody);

int main(void) {
    uint16_t f;

    init_tone();

    DDRD |= _BV(PD4);    /* PD4 as output: amplifier SHUTDOWN control */
    PORTD &= ~_BV(PD4);  /* Default amplifier state: shutdown (sleep) */

    DDRA &= ~(_BV(SW_PLAY) | _BV(SW_AMP)); /* PA0/PA1 as inputs */
    PORTA |= (_BV(SW_PLAY) | _BV(SW_AMP)); /* Enable pull-ups on PA0/PA1 */

    melody2freq(melody);

    for(;;) {
        if (bit_is_clear(PINA, SW_AMP)) {
            PORTD |= _BV(PD4);
        } else {
            PORTD &= ~_BV(PD4);
        }

        if (bit_is_clear(PINA, SW_PLAY)) {
            f = melody2freq(NULL);

            if (f == M2F_END) {
                melody2freq(melody);
                DDRD &= ~_BV(PD5); /* PD5 (OC1A) tri-stated: stop PWM to speaker */
                _delay_ms(1000);
            } else if (f != M2F_UNKOWN) {
                tone(f);
                DDRD |= _BV(PD5);  /* PD5 (OC1A) as output: enable PWM to speaker */
                _delay_ms(STEP_DELAY_MS);

                DDRD &= ~_BV(PD5); /* PD5 (OC1A) tri-stated: short gap between notes */
                _delay_ms(10);
            }
        } else {
            DDRD &= ~_BV(PD5);     /* PD5 (OC1A) tri-stated: stop PWM */
            PORTD &= ~_BV(PD5);
            melody2freq(melody);
        }
    }
}

void init_tone(void) {
    TCCR1A = _BV(COM1A0) | _BV(WGM10);
    TCCR1B = _BV(WGM13) | _BV(CS11);
}

void tone(uint16_t frequency) {
    OCR1A = (uint16_t)(F_CPU / (2 * 2 * TONE_PRESCALER) / frequency);
}

uint16_t melody2freq(const char *m) {
    static const char *melody_ptr;
    static uint16_t pos;
    static uint8_t scale_index;

    if(m != NULL){
        melody_ptr = m;
        pos = 0;
        return M2F_END;
    }

    if(melody_ptr[++pos] == '\0') return M2F_END;

    switch( melody_ptr[pos] ) {
        case 'c': case 'C': scale_index = ET_SCALE_C; break;
        case 'd': case 'D': scale_index = ET_SCALE_C + 2; break;
        case 'e': case 'E': scale_index = ET_SCALE_C + 4; break;
        case 'f': case 'F': scale_index = ET_SCALE_C + 5; break;
        case 'g': case 'G': scale_index = ET_SCALE_C + 7; break;
        case 'a': case 'A': scale_index = ET_SCALE_C + 9; break;
        case 'b': case 'B': scale_index = ET_SCALE_C + 11; break;
        default: return M2F_UNKOWN;
    }

    if(melody_ptr[pos] > 'Z') {
         scale_index += 12;
    }
    return et_scale[scale_index];
}
