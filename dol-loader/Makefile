# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# Tested and working with `powerpc-eabi-gcc (devkitPPC release 29-1) 6.3.0`.
# You might have to hack if your setup isn't similar - this isn't totally
# portable [yet], and it's a mess.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

BOLD=$(shell tput bold)
NORMAL=$(shell tput sgr0)

BASEDIR		:= $(PWD)/../

OBJCOPY		:= powerpc-eabi-objcopy
LD		:= powerpc-eabi-ld
CC		:= powerpc-eabi-gcc

# Where to write output .GCI files
OUT_DIR 	:= $(PWD)

# The base FGX garage GCI to modify and prepare with the exploit
BASE_GCI 	:= $(PWD)/8P-GFZP-fzr0000C1404EB11BF5E69E5B.dat_00.gci

# Paths to tools
PREPARE_ACE 	:= $(PWD)/py/prepare-ace.py
MAKE_DATA_GCI 	:= $(PWD)/py/make-data-gci.py

# GCC flags
C_CCFLAGS	:= -s -Qn -Wa,-mregnames -c
S_CCFLAGS	:= -mregnames -c

# Symbol declarations for functions in-memory during runtime
FGX_SYMBOLS	:= fgx.sym

# Linkerscript
P_LS		:= fgx.ld

# Linker flags
P_LDFLAGS 	:= --just-symbols=$(FGX_SYMBOLS) -T $(P_LS)

# -----------------------------------------------------------------------------
all:
	@clear

# Compile the main payload, then prepare a garage file with the exploit and
# payload for loading/executing some DOL from memory card. If you're building
# a DOL to-be-run by this, recall that this particular loader links against
# FGX functions, so you'll need to make sure that code is compiled to run
# somewhat higher in memory (ie. I've been using 0x81000100 as the entrypoint).
#
# In order to create a DOL to load with this, you'll have to use something
# like `make-data-gci.py` in hosaka-corp/fgx-re. Currently, the code looks
# for a `boot.dol` file on memory card.

	@echo -e "$(BOLD)[Makefile] Build the main payload$(NORMAL)"
	$(CC) $(C_CCFLAGS) src/main.c -o main.o
	$(CC) $(S_CCFLAGS) src/entry.S -o entry.o
	$(LD) $(P_LDFLAGS) entry.o main.o -o test.elf
	$(OBJCOPY) -O binary --only-section=.text test.elf test.bin
	$(PREPARE_ACE) $(BASE_GCI) test.bin $(OUT_DIR)/fgx-dol-loader.gci

	@echo -e "$(BOLD)[Makefile] All done!$(NORMAL)"

.PHONY: clean
clean:
	@echo -e "$(BOLD)[Makefile] Cleanup ...$(NORMAL)"
	@rm -f {main,entry}.o test.{elf,bin}
