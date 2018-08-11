#include "fgx_link.h"

#define millisecs(x)		((uint64_t)(x) * (162000000u / 4000))

#define CARDMOUNT_BASE		0x81400000 // 0xA000 bytes
#define DOL_HANDLE_BASE		0x816ff100 // ~0x20 bytes

/* ----------------------------------------------------------------------------
 * Some generic functions */

/* Write garbage to the framebuffer and loop forever. Currently using this
 * function to determine whether or not we find the LR that we need to
 * return to when cleaning up in src/entry.S */
uint32_t die(void){
	unsigned int *fb = (unsigned int*)0x81200000;
	for (int i = 0; i < 0x8000; i++)
		fb[i] = 0x1E;

	do
	{
		VISetNextFramebuffer((void*)fb);
		VIFlush();
	} while (1 == 1);

}

/* Sleep for some amount of milliseconds. This probably has corner cases.
 * Also, I don't think that these casts to 64 bits are necessary.  */
void sleep(uint32_t ms)
{
	uint32_t ts, cur, diff, i = 0;
	ts = OSGetTick();

	do
	{
		cur = OSGetTick();
		diff = ~((uint64_t)ts - (uint64_t)cur) + 1;

	} while(diff < millisecs(ms));
}


/* ----------------------------------------------------------------------------
 * .dol loading code live here. This set of gadgets is pulled almost directly
 * from FIX94's DOL loader code. See https://github.com/FIX94/007-exploit-gc
 * and others for details. FIX saves the day again :^)
 */


static struct card_struct *dol_handle = (struct card_struct *)DOL_HANDLE_BASE;

// Name of some GCI on card holding the DOL payload to load
static unsigned char dol_filename[] = "boot.dol\x00";

static void *mount_area = (void*)CARDMOUNT_BASE;

static uint32_t mount_res = 0xAAAAAAAA;
void mountcb(int32_t slot, int32_t res){ mount_res = res; }

static uint32_t read_res = 0xAAAAAAAA;
void readcb(int32_t slot, int32_t res){ read_res = res; }

static uint8_t scratch_area[0x200] = {};
static struct dol_hdr hdr;

void *_memset(void *ptr, int c, int size)
{
	char* ptr2 = ptr;
	while(size--) *ptr2++ = (char)c;
	return ptr;
}
void sync_cache(void *p, uint32_t n)
{
	uint32_t start, end;

	start = (uint32_t)p & ~31;
	end = ((uint32_t)p + n + 31) & ~31;
	n = (end - start) >> 5;

	while (n--) {
		asm("dcbst 0,%0 ; icbi 0,%0" : : "b"(p));
		p += 32;
	}
	asm("sync ; isync");
}
static void sync_before_read(void *p, uint32_t n)
{
	uint32_t start, end;

	start = (uint32_t)p & ~31;
	end = ((uint32_t)p + n + 31) & ~31;
	n = (end - start) >> 5;

	while (n--) {
		asm("dcbf 0,%0" : : "b"(p));
		p += 32;
	}
	asm("sync");
}
void readAlign(uint8_t *section_addr, uint32_t section_len, uint32_t section_off)
{
	uint32_t tmp_len;
	uint32_t card_off = section_off & (~0x1ff);
	uint32_t scratch_off = section_off - card_off;

	if (scratch_off > 0){
		CARDReadAsync(dol_handle, scratch_area, 0x200, card_off, readcb);
		while (read_res != 0) {};
		read_res = 0xAAAAAAAA;
		if (section_len > 0x200)
			tmp_len = 0x200 - scratch_off;
		else
			tmp_len = section_len - scratch_off;
		_memcpy(section_addr, scratch_area + scratch_off, tmp_len);
		sync_cache(section_addr, tmp_len);
		card_off += 0x200;
		section_addr += tmp_len;
		section_len -= tmp_len;
	}
	while (section_len > 0)
	{
		CARDReadAsync(dol_handle, scratch_area, 0x200, card_off, readcb);
		while (read_res != 0) {};
		read_res = 0xAAAAAAAA;
		if (section_len > 0x200)
			tmp_len = 0x200;
		else
			tmp_len = section_len;
		_memcpy(section_addr, scratch_area, tmp_len);
		sync_cache(section_addr, tmp_len);
		card_off += 0x200;
		section_addr += tmp_len;
		section_len -= tmp_len;
	}
}

void load_dol_from_card(void)
{
	uint32_t i;
	uint16_t hi, lo;

	OSDisableScheduler();
	OSStopAudioSystem();

	/* Mount the card in slot A and get a handle to the DOL */

	CARDMountAsync(0, mount_area, 0, mountcb);
	while (mount_res != 0) {};
	CARDOpen(0, (unsigned char*)&dol_filename, dol_handle);

	/* Load the DOL header */

	CARDReadAsync(dol_handle, scratch_area, 0x200, 0, readcb);
	while (read_res != 0) {};
	read_res = 0xAAAAAAAA;
	_memcpy(&hdr, scratch_area, 0x100);
	sync_cache(&hdr, 0x100);

	/* Actually load the DOL into memory */

	for (i=0; i < 7; i++)
	{
		if ((!hdr.text_size[i]) || (hdr.text_addr[i] < 0x100))
			continue;
		readAlign((uint8_t*)hdr.text_addr[i], hdr.text_size[i],
				hdr.text_off[i]);
	}
	for (i=0; i < 11; i++)
	{
		if ((!hdr.data_size[i]) || (hdr.data_addr[i] < 0x100))
			continue;
		readAlign((uint8_t*)hdr.data_addr[i], hdr.data_size[i],
				hdr.data_off[i]);
	}

	hi = (hdr.entrypt >> 16) & 0xffff;
	lo = hdr.entrypt & 0xffff;

	/* This might not be necessary because the libogc crt0 should be
	 * sufficient to totally re-initialize the state of everything */

	CARDUnmount(0);
	
	/* Branch into the DOL entrypoint */

	register int e asm("r3") = hdr.entrypt;
	__asm__ volatile ( "mtlr r3; blr;" :::);
}

// This is the main function we branch into from entry.S
void do_payload(void) { load_dol_from_card(); }
