#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define TEST_FILE		"test.gci"
#define OUTPUT_FILE		"test_00_replay_region.bin"
#define COMPRESSED_DATA_OFFSET	0x20A0

/* Structure of un-obfuscated replay data. See yoshifan's research:
 * https://github.com/yoshifan/fzerogx-docs */
struct replay_entry {
	uint8_t mask;
	int8_t steer_x;
	int8_t steer_y;
	int8_t strafe;
	uint8_t accel;
	uint8_t brake;
	uint8_t frames;
} __attribute__((__packed__));


/* This seems like the function responsible for decompressing bytes.
 * I'm pretty sure the behavior is correct. */
uint32_t func_802aefb8(void *compressed_base, uint32_t *total_iterations,
		uint32_t num_iterations) {
	printf("func_802aefb8(..., *total_iter=0x%08x, num_iter=0x%02x) = ",
			*total_iterations, num_iterations);

	uint32_t result = 0;
	int ctr = num_iterations;
	uint32_t base_offset;
	uint32_t mask;
	uint32_t input_val;
	void *input_ptr;

	if (num_iterations == 0) // this should always be > 0
		return -1;

	while (ctr != 0) {
		base_offset = (*total_iterations >> 3) & 0x1fffffff;

		input_ptr = compressed_base + base_offset;
		input_val = *(uint8_t*)input_ptr;

		mask = *total_iterations & 0x00000007;
		mask = 1 << (mask & 0x1F); // what is the 0x1F doing here even

		if (mask & input_val)
			result = result | (1 << ((num_iterations -1) & 0x1F));

		num_iterations--;
		*total_iterations = *total_iterations + 1;
		ctr--;
		//printf("base_off=0x%08x, mask=0x%08x, input_val=0x%02x, total_iter=0x%08x\n",
		//	base_offset, mask, input_val, *total_iterations);
	}

	printf("0x%08x\n", result);
	return result;
}


void func_80596414(unsigned char *gci_data, uint32_t *num_bits){
	uint32_t res;

	uint8_t r28_unk0, r28_unk1, r28_unk2, r28_unk3, r28_unk4;
	uint32_t r24_loop1, r31_loop1, r18_loop2, r25_loop3;
	uint32_t r23_unk1;
	uint32_t r20_unk1 = 5; // I actually don't know why this is 5

	res = func_802aefb8(gci_data, num_bits, 8);
	res = func_802aefb8(gci_data, num_bits, 7);
	res = func_802aefb8(gci_data, num_bits, 6);
	res = func_802aefb8(gci_data, num_bits, 32);
	res = func_802aefb8(gci_data, num_bits, 32);
	// stw r3, 0(r6=801a63c0) (???)
	res = func_802aefb8(gci_data, num_bits, 5);
	r31_loop1 = res; // mr r31, r3
	res = func_802aefb8(gci_data, num_bits, 3);
	// sth r3, 0x8(r5=803ffd80) (???)
	res = func_802aefb8(gci_data, num_bits, 2);
	res = func_802aefb8(gci_data, num_bits, 1);
	// rlwinm r21, r3, 0, 24, 31 (???)
	res = func_802aefb8(gci_data, num_bits, 7);
	// rlwinm r22, r3, 0, 24, 31 (???)

	r23_unk1 = 0;
	r24_loop1 = 0;  // li r24, 0

	while (r24_loop1 < r31_loop1) { //cmplw r24, r31; blt 0x80596530

		res = func_802aefb8(gci_data, num_bits, 1);
		r28_unk0 = (uint8_t)res & 0xFF; //stb r3, 0x0000(r28=8039b560)

		res = func_802aefb8(gci_data, num_bits, 6);
		r28_unk1 = (uint8_t)res & 0xFF; //stb r3, 0x0001(r28=8039b560)

		if (r20_unk1 > 3) { //cmplwi r20, 3; blt- 0x80596574
			res = func_802aefb8(gci_data, num_bits, 5);
			r28_unk4 = (uint8_t)res & 0xFF; //stb r3, 0x0004(r28=8039b560)
		}

		if (r20_unk1 > 2) { //cmplwi r20, 2; blt- 0x80596590
			res = func_802aefb8(gci_data, num_bits, 7);
			r28_unk3 = (uint8_t)res & 0xFF; // stb r3, 0x0003(r28=8039b560)
		}

		if (r28_unk0 != 0) { // lbz r0, 0(r28=8039b560); cmplwi r0, 0; beq- 0x805966b4
			res = func_802aefb8(gci_data, num_bits, 2);
			r28_unk2 = (uint8_t)res & 0xFF; // stb r3, 0x0002(r28=8039b560)

			if (r20_unk1 < 2) { //cmplwi r20, 2; bge- 0x805965cc
				res = func_802aefb8(gci_data, num_bits, 7);
				r28_unk3 = (uint8_t)res & 0xFF; // stb r3, 0x0003(r28=8039b560)
			}

			res = func_802aefb8(gci_data, num_bits, 1);

			if ( (res & 0x000000FF) != 0) { // rlwinm. r0, r3, 0 24, 31 (???)
				r18_loop2 = 0; // li r18, 0
				while (r18_loop2 < 33216) {
					res = func_802aefb8(gci_data, num_bits, 8);
					//rlwinm r19, r3, 0, 24, 31
					r18_loop2++;
				}
			}

			r23_unk1++;
			r24_loop1++;
		}
		else if (r28_unk0 == 0) {
			r28_unk2 = 0;
			r28_unk3 = 0;
			r24_loop1++; // addi r24, r24, 1
		}
	}

	if (r20_unk1 > 4) { //cmplwi r20, 4; blt- 0x8059671c
		// rlwinm r24, r23, 0, 24, 31 (???)
		r25_loop3 = 0; // li r25, 0
		while (r25_loop3 < r24_loop1) { // cmpw r25, r24; blt+ 0x805966f8
			res = func_802aefb8(gci_data, num_bits, 1);
			// stb r3, 0x003c(r19=803f39b8)
			// addi r19, r19, 1
			r25_loop3++; // addi r25, r25, 1
		}
	}

	// rlwinm r24, r23, 0, 24, 31 (???)
	r25_loop3 = 0; // li r25, 0
	while (r25_loop3 < r24_loop1) { // cmpw r25, r24; blt+ 0x80596730
		res = func_802aefb8(gci_data, num_bits, 2);
		//addi r0, r3, 1
		r25_loop3++; // addi r25, r25, 1
		//stb r0, 0x0038 (r19=803f39b8)
		//addi r19, r19, 1
	}

	if (r20_unk1 >= 5) { //clmpwi r20, 5; blt- 0x8059677c
		res = func_802aefb8(gci_data, num_bits, 20);
	}

	// ...
	// blr
}




/* This function allocates an array of `struct replay_entry` and returns
 * a pointer to the filled array after all bytes have been decoded.
 * Takes a pointer to some `array_length` in order to pass the number of
 * entries back to `main()`. */
struct replay_entry *func_80596810(unsigned char *gci_data,
		uint32_t *num_bits, uint32_t *replay_array_length){

	uint32_t res, idx, arrlen;
	struct replay_entry *arr;

	uint32_t r20_loop1, r21_loop2, r19_loop3;
	uint16_t r4_unk1;

	res = func_802aefb8(gci_data, num_bits, 8);

	r20_loop1 = 0; // li r20, 0
	r4_unk1 = (uint16_t)res; //sth r3, -0x0110(r4=81291380)

	while (r20_loop1 < r4_unk1) { //cmpw r20, r0; blt+ 0x805968cc
		res = func_802aefb8(gci_data, num_bits, 14);
		res = func_802aefb8(gci_data, num_bits, 14);
		res = func_802aefb8(gci_data, num_bits, 4);
		res = func_802aefb8(gci_data, num_bits, 5);
		res = func_802aefb8(gci_data, num_bits, 5);
		res = func_802aefb8(gci_data, num_bits, 5);
		res = func_802aefb8(gci_data, num_bits, 5);
		res = func_802aefb8(gci_data, num_bits, 5);

		r19_loop3 = 0; // li r19, 0
		// li r24, 0 (???)
		// ...

		r21_loop2 = 1; // lbz r0, 0 (r21) (don't know where this is from)
		while (r19_loop3 < r21_loop2) { //cmpw r19, r0; blt+ 0x80596a18
			res = func_802aefb8(gci_data, num_bits, 32);
			res = func_802aefb8(gci_data, num_bits, 32);
			res = func_802aefb8(gci_data, num_bits, 32);
			res = func_802aefb8(gci_data, num_bits, 32);
			res = func_802aefb8(gci_data, num_bits, 32);
			res = func_802aefb8(gci_data, num_bits, 32);
			r19_loop3++;
		}

		res = func_802aefb8(gci_data, num_bits, 32);
		res = func_802aefb8(gci_data, num_bits, 32);
		res = func_802aefb8(gci_data, num_bits, 32);
		res = func_802aefb8(gci_data, num_bits, 32);
		res = func_802aefb8(gci_data, num_bits, 32);
		res = func_802aefb8(gci_data, num_bits, 32);
		r20_loop1++;
	}

	// Get the number of entries in the decompressed replay array
	arrlen = func_802aefb8(gci_data, num_bits, 14);

	/* Write the array length back to the caller, then allocate an
	 * array to return after we're done writing decompressed data */

	*replay_array_length = arrlen; // write array length back to caller
	arr = malloc((sizeof(struct replay_entry) * (arrlen+0x10)));
	memset(arr, 0x00, (sizeof(struct replay_entry) * (arrlen+0x10)));
	struct replay_entry *cur = arr;


	printf("-------------------- replay array --------------------\n");
	idx = 0;
	while (idx <= arrlen){
		cur->mask    = func_802aefb8(gci_data, num_bits, 8);
		cur->strafe  = func_802aefb8(gci_data, num_bits, 8);
		cur->accel   = func_802aefb8(gci_data, num_bits, 7);
		cur->brake   = func_802aefb8(gci_data, num_bits, 7);
		cur->frames  = func_802aefb8(gci_data, num_bits, 8);
		cur->steer_x = func_802aefb8(gci_data, num_bits, 8);
		cur->steer_y = func_802aefb8(gci_data, num_bits, 8);
		cur++;
		idx++;
	}

	// ...
	// blr
	return arr;
}


int main() {
	FILE *out, *in;
	int pos;

	uint32_t bit_counter = 0x00;
	uint32_t array_size;
	unsigned char *gci_base;
	struct replay_entry *replay_array;

	/* Pull compressed replay data into memory (overcommit by 0x1000 bytes
	 * in case we do something horrible to memory). */

	in = fopen(TEST_FILE, "rb");
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

	func_80596414(gci_base, &bit_counter);


	/* A lot of different other things happen here (we go up in the call
	 * stack) that may or may not be relevant. Eventually we enter the
	 * function at 0x80596810 -- seems like it's responsible for actually
	 * building the replay array that encodes some inputs. */

	replay_array = func_80596810(gci_base, &bit_counter, &array_size);


	/* Write the replay array to a file, then clean up and exit. */

	out = fopen(OUTPUT_FILE, "wb");
	if (out == NULL)
		exit(-1);
	fwrite(replay_array, sizeof(struct replay_entry), array_size+1, out);
	fclose(out);
	printf("[*] Wrote 0x%x replay array entries\n", array_size+1);


	free(gci_base);
	free(replay_array);
}
