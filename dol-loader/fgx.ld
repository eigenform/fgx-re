MEMORY
{
	RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 24M
	SHELLCODE (rwx) : org = 0x801af5d0, l = 10K
}

SECTIONS
{
	.text :
	{
		entry.o
		. += 0x20;
		. = ALIGN(0x40);
		main.o(.text)
		. += 0x20;
		. = ALIGN(0x40);
		main.o(.data)
		main.o(.sdata)
		. += 0x20;
		. = ALIGN(0x40);
		main.o(.bss)
		. += 0x20;
		. = ALIGN(0x40);
	} >SHELLCODE
}
