#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "fgx_compression.h"

#define TEST_FILE		"test.gci"
#define OUTPUT_FILE		"test_00_replay_region.bin"
#define COMPRESSED_DATA_OFFSET	0x20A0

int main(int argc, char* argv[]) {
	if (argc < 3) {
		printf("usage: fgx-decompress-replay <input replay GCI> <output file>\n");
		printf("  Given some FZGX replay file, decompress the contents and\n");
		printf("  write the raw, in-memory replay array to some file.\n");
		return -1;
	}

	FILE *out, *in;
	int pos;

	uint32_t bit_counter = 0x00;
	uint32_t array_size;
	unsigned char *gci_base;
	struct replay_entry *replay_array;

	/* Pull compressed replay data into memory (overcommit by 0x1000 bytes
	 * in case we do something horrible to memory). */

	in = fopen(argv[1], "rb");
	if (in == NULL)
		exit(-1);
	fseek(in, 0, SEEK_END);
	int replay_size = ftell(in);
	fseek(in, COMPRESSED_DATA_OFFSET, SEEK_SET);
	printf("[*] Replay data starts at offset 0x%x in GCI\n",
			COMPRESSED_DATA_OFFSET);
	printf("[*] Reading 0x%x bytes of replay data...\n",
			replay_size - COMPRESSED_DATA_OFFSET);
	gci_base = malloc(replay_size + 0x1000);
	fread(gci_base, replay_size + 0x1000, 1, in);
	fclose(in);

	/* The counter of decoded bits starts in the function at 0x80596414.
	 * Not entirely sure what the purpose of this function is [yet].  */

	decompress_header(gci_base, &bit_counter);

	/* A lot of different other things happen here (we go up in the call
	 * stack) that may or may not be relevant. Eventually we enter the
	 * function at 0x80596810 -- seems like it's responsible for actually
	 * building the replay array that encodes some inputs. */

	replay_array = decompress_array(gci_base, &bit_counter, &array_size);

	/* Write the replay array to a file, then clean up and exit. */

	out = fopen(argv[2], "wb");
	if (out == NULL)
		exit(-1);
	fwrite(replay_array, sizeof(struct replay_entry), array_size+1, out);
	fclose(out);
	printf("[*] Wrote 0x%x replay array entries\n", array_size+1);


	free(gci_base);
	free(replay_array);
}
