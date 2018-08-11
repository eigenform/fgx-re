#include <stdint.h>

struct card_struct
{
    int chan;
    int fnum;
    int offset;
    int length;
    uint16_t block;
};

struct dol_hdr {
	uint32_t text_off[7];
	uint32_t data_off[11];
	uint32_t text_addr[7];
	uint32_t data_addr[11];
	uint32_t text_size[7];
	uint32_t data_size[11];
	uint32_t bss_addr;
	uint32_t bss_size;
	uint32_t entrypt;
	uint32_t pad[7];
};

typedef void (*SICallback)(int32_t,uint32_t);
typedef void (*CARDCallback)(int32_t,int32_t);

void* _malloc(uint32_t size);
void _free(void *ptr);

uint32_t SI_GetTypeAsync(int32_t chn, SICallback cb);
uint32_t SI_GetType(int32_t chn);

uint32_t SI_Transfer(int32_t chn, void *out, uint32_t out_len, void *in,
	uint32_t in_len, SICallback cb, uint32_t us_delay);

static uint32_t __si_transfer(int32_t chan, void *out, uint32_t out_len, void *in,
	uint32_t in_len, SICallback cb);

void ICInvalidateRange(void *addr, uint32_t len);
void DCFlushRange(void *addr, uint32_t len);

uint32_t GetTypeWrapper(int32_t chn);

uint32_t OSGetTick(void);

void OSDisableInterrupts(void);
void OSEnableInterrupts(void);

void VISetNextFramebuffer(void *fb);

// I think there are no args?
void VIFlush(void);

void TRK_flush_cache(void *addr, uint32_t size);

void _sprintf(void *buf, void* fmt, uint32_t val1,
		uint32_t val2, uint32_t val3, uint32_t val4, uint32_t val5);

void _memcpy(void *dest, void *source, uint32_t size);

// This will reset the game!
void __start(void);

int CARDOpen(int chan, const char *path, struct card_struct *inf);
int CARDClose(struct card_struct *inf);
int32_t CARDInit(char *gamecode, char *company);

int32_t CARDUnmount(int32_t slot);
int32_t CARDMountAsync(int32_t slot, void *work_area,
		CARDCallback detach, CARDCallback attach);

int32_t CARDWriteAsync(struct card_struct *cs, void *buf, uint32_t size,
		uint32_t off, CARDCallback cb);

int32_t CARDCreateAsync(int32_t slot, char *filename, uint32_t size,
	       struct card_struct *file, CARDCallback cb);	

int32_t CARDReadAsync(struct card_struct *cs, void *buf,
		uint32_t len, uint32_t off, CARDCallback cb);

void OSDisableScheduler(void);
void OSStopAudioSystem(void);
void GXSetDrawDone(void);

void *MemAlloc(uint32_t id, uint32_t size);
