#include <util/twi.h>

//from C7 lab
#define I2C_READ    1
#define I2C_WRITE   0

void init_i2c_master(void)
{
	/* F_SCL = F_CPU/120 = 100kHz */
	TWBR = 0x34;
	TWSR = 0x00;
}

void i2c_start(void)
{
	TWCR = _BV(TWINT) | _BV(TWSTA) | _BV(TWEN);
	while(!(TWCR & _BV(TWINT)));
}

void i2c_stop(void)
{
	TWCR = _BV(TWINT) | _BV(TWSTO) | _BV(TWEN);
}

void i2c_tx(uint8_t b)
{
	TWDR = b;
	TWCR = _BV(TWINT) | _BV(TWEN);
	while(!(TWCR & _BV(TWINT)));
}

uint8_t i2c_rx_ack(void)
{
	TWCR = _BV(TWINT) | _BV(TWEN) | _BV(TWEA);
	while(!(TWCR & _BV(TWINT)));
	return TWDR;
}

uint8_t i2c_rx_nack(void)
{
	TWCR = _BV(TWINT) | _BV(TWEN);
	while(!(TWCR & _BV(TWINT)));
	return TWDR;
}