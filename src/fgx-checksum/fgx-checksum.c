#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define BLOCK_SIZE	0x2000
#define DENTRY_SIZE	0x40
struct dentry {
	uint8_t gamecode[4];
	uint8_t makercode[2];
	uint8_t unused_a;
	uint8_t bi_flags;
	char filename[0x20];
	uint8_t modtime[4];
	uint8_t image_offset[4];
	uint8_t icon_fmt[2];
	uint8_t anim_speed[2];
	uint8_t permissions;
	uint8_t copy_counter;
	uint8_t first_block[2];
	uint16_t block_count;
	uint8_t unused_b[2];
	uint32_t comments_addr;
}__attribute__((__packed__));

#define DATA_SIZE	((BLOCK_SIZE * 4) - 2)
struct fgx_gci {
	struct dentry dentry;
	uint16_t checksum;
	unsigned char data[DATA_SIZE];
}__attribute__((__packed__));

extern void hexdump(char *desc, void *addr, int len);


/* Effectively pulled from the following projects:
 *	- https://github.com/bobjrsenior/SMB_Checksum_Fixer 
 *	- https://github.com/suloku/gcmm
 *
 * This seems to work okay in Dolphin while modifying GCIs on my box.
 * Unclear how the serial numbers for raw memory cards play into this.
 */
uint16_t fzgx_fix_checksum(struct fgx_gci *gci){
	uint16_t checksum = 0xFFFF;
	for (int i = 0; i < DATA_SIZE; i++) {
		checksum ^= gci->data[i];
		for (int j = 0; j < 8; j++) {
			if (checksum & 1){
				checksum = (checksum >>= 1) ^ 0x8408;
			}
			else checksum >>= 1;
		}

	}
	return (checksum ^ 0xFFFF);
}

/* Just a hacky solution for now. */
int main(int argc, char* argv[]) {
	if (argc < 2) {
		printf("usage: fgx-checksum <input GCI>\n");
		printf("  Given some FZGX savedata GCI, fix the checksum data.\n");
		printf("  WARNING: This will write on the file you point it at!\n");
		return -1; 
	}

	FILE *in, *out;
	int pos;
	struct fgx_gci *gci;

	/* Read the input GCI */
	in = fopen(argv[1], "rb");
	if (in == NULL)
		exit(-1);
	fseek(in, 0, SEEK_END);
	int gci_size = ftell(in);
	fseek(in, 0, SEEK_SET);
	if (gci_size != (sizeof(*gci))) { 
		printf("[*] FZGX savedata GCI should be 0x%x bytes (got 0x%x bytes)\n",
				sizeof(*gci), gci_size);
		exit(-1);
	}
	printf("[*] Reading 0x%x bytes ...\n", gci_size);
	gci = malloc(sizeof(*gci));
	fread(gci, sizeof(*gci), 1, in);
	fclose(in);

	uint16_t current_checksum = gci->checksum;
	uint16_t new_checksum = fzgx_fix_checksum(gci);
	if (current_checksum != new_checksum) {
		gci->checksum = new_checksum;
		out = fopen(argv[1], "wb");
		fwrite(gci, sizeof(*gci), 1, out);
		fclose(out);
		printf("[*] Fixed checksum ([0x%04x] -> [0x%04x])\n",
				current_checksum, new_checksum);
	}
	else printf("[*] Checksum for GCI is already valid!\n");

	fclose(in);
	free(gci);
}
