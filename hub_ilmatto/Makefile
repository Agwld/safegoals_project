# --- CONFIGURATION ---
MCU      = atmega644p
F_CPU    = 12000000
PROGRAMMER = usbasp

# --- DIRECTORIES ---
SRCDIR   = src
INCDIR   = include
OBJDIR   = obj
BINDIR   = bin

# --- TOOLS ---
CC       = avr-gcc
OBJCOPY  = avr-objcopy
AVRDUDE  = avrdude

# --- FLAGS ---
CFLAGS   = -mmcu=$(MCU) -DF_CPU=$(F_CPU)UL -Os -I$(INCDIR)
CFLAGS  += -Wall -Wextra -Wstrict-prototypes
CFLAGS  += -funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums

# --- SOURCES & OBJECTS ---
# Automatically find all .c files in src/ directory
SOURCES  = $(wildcard $(SRCDIR)/*.c)
OBJECTS  = $(patsubst $(SRCDIR)/%.c, $(OBJDIR)/%.o, $(SOURCES))
TARGET   = $(BINDIR)/hub_firmware

# --- BUILD RULES ---
all: $(TARGET).hex

# 1. Compile .c to .o
$(OBJDIR)/%.o: $(SRCDIR)/%.c
	@mkdir -p $(OBJDIR)
	@echo "Compiling $<..."
	$(CC) $(CFLAGS) -c $< -o $@

# 2. Link .o files into .elf
$(TARGET).elf: $(OBJECTS)
	@mkdir -p $(BINDIR)
	@echo "Linking..."
	$(CC) $(CFLAGS) $(OBJECTS) -o $@

# 3. Convert .elf to .hex
$(TARGET).hex: $(TARGET).elf
	@echo "Creating HEX file..."
	$(OBJCOPY) -O ihex -R .eeprom $< $@
	@echo "Build Complete: $@"

# --- UPLOAD COMMANDS ---
# Flash using USBASP (Standard ISP)
flash: $(TARGET).hex
	$(AVRDUDE) -c $(PROGRAMMER) -p $(MCU) -U flash:w:$<:i

# --- CLEANUP ---
clean:
	rm -rf $(OBJDIR) $(BINDIR)
	@echo "Cleaned build files."

# Phony targets identify commands that aren't files
.PHONY: all flash clean