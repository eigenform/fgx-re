#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define TEST_FILE "test_00.bin"
#define OUTPUT_FILE "test_00_replay_region.bin"

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
	printf("func_802aefb8(..., *total_iter=0x%08x, num_iter=0x%02x) = ", *total_iterations, num_iterations);

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
	}

	printf("0x%08x\n", result);
	return result;
}


/* `main()` here is a test representing the start of the function at
 * 0x80596414, which makes these passes over the beginning of obfuscated GCI
 * data. These are just to test the output of func_802aefb8 against expected
 * values.
 *
 * test.bin is yoshifan's `8P-GFZE-fzr000035804D31D70EE97E77.dat.gci` file
 * with the head chopped off (the obfuscated data starts at 0x20a0); do:
 *
 * $ dd if=8P-GFZE-fzr000035804D31D70EE97E77.dat.gci of=test.bin bs=1 \
 * 	skip=$((0x20a0))
 *
 * Needless to say: this is a messy representation of the process, and it's
 * probably wrong in the sense that it's probably not a general-enough
 * representation of this whole process [yet!]. Some of the loop counters here
 * may be particular to/computed specifically for handling the input from
 * 8P-GFZE-fzr000035804D31D70EE97E77 in particular -- mostly because I haven't
 * figured out where they're set/what they're dependent on.
 *
 * Note that, in the actual code, we always `li r5, <some number` for passing
 * the `num_iterations` argument to func_802aefb8 (so at least these
 * function calls are correct in that sense).
 */
int main() {
	uint32_t res;
	uint32_t *total_obfuscated = malloc(sizeof(uint32_t));
	*total_obfuscated = 0x00;

	uint32_t r31_counter1;
	uint32_t r24_counter1;

	uint32_t r25_counter4;
	uint32_t r24_counter4;


	uint8_t r28_unk0;
	uint8_t r28_unk1;
	uint8_t r28_unk2;
	uint8_t r28_unk3;
	uint8_t r28_unk4;

	uint16_t r4_off_0x0110;

	uint32_t r20_counter2 = 5; // I actually don't know why this is 5
	uint32_t r20_counter7;
	uint32_t r23_counter3;
	uint32_t r23_counter8;

	uint32_t r21_counter9;
	uint32_t r19_counter9;

	uint32_t r27_counter10;

	uint32_t r18_counter11;

	uint32_t current_array_index;
	uint32_t replay_array_length;
	uint32_t replay_bytes_counter;


	unsigned char *gci_data = malloc(0x4000);
	FILE *fp = fopen(TEST_FILE, "rb");
	if (fp == NULL)
		exit(-1);
	fread(gci_data, 0x4000,1,fp);
	fclose(fp);

	FILE *out;

/* -------- Function 0x80596414 00_Do_Decompression0? ---------------------- */
loc_80596450:
	res = func_802aefb8(gci_data, total_obfuscated, 8);
	res = func_802aefb8(gci_data, total_obfuscated, 7);
	res = func_802aefb8(gci_data, total_obfuscated, 6);
	res = func_802aefb8(gci_data, total_obfuscated, 32);
	// SetTRKConnected();
	res = func_802aefb8(gci_data, total_obfuscated, 32);
	// stw r3, 0(r6=801a63c0) (???)
	res = func_802aefb8(gci_data, total_obfuscated, 5);
	r31_counter1 = res; // mr r31, r3
	res = func_802aefb8(gci_data, total_obfuscated, 3);
	// sth r3, 0x8(r5=803ffd80) (???)
	res = func_802aefb8(gci_data, total_obfuscated, 2);
	res = func_802aefb8(gci_data, total_obfuscated, 1);
	// rlwinm r21, r3, 0, 24, 31 (???)
	res = func_802aefb8(gci_data, total_obfuscated, 7);
	// rlwinm r22, r3, 0, 24, 31 (???)

	r23_counter3 = 0;
	r24_counter1 = 0;  // li r24, 0
	r27_counter10 = 0; // li r27, 0

	while (r24_counter1 < r31_counter1) { //cmplw r24, r31; blt 0x80596530
		res = func_802aefb8(gci_data, total_obfuscated, 1);
		r28_unk0 = (uint8_t)res & 0xFF; //stb r3, 0x0000(r28=8039b560)
		res = func_802aefb8(gci_data, total_obfuscated, 6);

		r28_unk1 = (uint8_t)res & 0xFF; //stb r3, 0x0001(r28=8039b560)

		if (r20_counter2 > 3) { //cmplwi r20, 3; blt- 0x80596574
			res = func_802aefb8(gci_data, total_obfuscated, 5);
			r28_unk4 = (uint8_t)res & 0xFF; //stb r3, 0x0004(r28=8039b560)
		}

		if (r20_counter2 > 2) { //cmplwi r20, 2; blt- 0x80596590
			res = func_802aefb8(gci_data, total_obfuscated, 7);
			r28_unk3 = (uint8_t)res & 0xFF; // stb r3, 0x0003(r28=8039b560)
		}

		if (r28_unk0 != 0) { // lbz r0, 0(r28=8039b560); cmplwi r0, 0; beq- 0x805966b4
			res = func_802aefb8(gci_data, total_obfuscated, 2);
			r28_unk2 = (uint8_t)res & 0xFF; // stb r3, 0x0002(r28=8039b560)

			if (r20_counter2 < 2) { //cmplwi r20, 2; bge- 0x805965cc
				res = func_802aefb8(gci_data, total_obfuscated, 7);
				r28_unk3 = (uint8_t)res & 0xFF; // stb r3, 0x0003(r28=8039b560)
			}

			res = func_802aefb8(gci_data, total_obfuscated, 1);

			if ( (res & 0xFF000000) != 0) { // rlwinm. r0, r3, 0 24, 31 (???)
				r18_counter11 = 0; // li r18, 0
				while (r18_counter11 < 33216) {
					res = func_802aefb8(gci_data, total_obfuscated, 8);
					//rlwinm r19, r3, 0, 24, 31
					//func_801f154c();
					r18_counter11++;
				}
			}

			// A bunch of things that I don't understand happen here
			// ...

			r23_counter3++;
			r24_counter1++;
		}
		else if (r28_unk0 == 0) {
			r28_unk2 = 0;
			r28_unk3 = 0;
			r24_counter1++; // addi r24, r24, 1
		}
	}

	if (r20_counter2 > 4) { //cmplwi r20, 4; blt- 0x8059671c
		// rlwinm r24, r23, 0, 24, 31 (???)
		r25_counter4 = 0; // li r25, 0
		while (r25_counter4 < r24_counter1) { // cmpw r25, r24; blt+ 0x805966f8
			res = func_802aefb8(gci_data, total_obfuscated, 1);
			// stb r3, 0x003c(r19=803f39b8)
			// addi r19, r19, 1
			r25_counter4++; // addi r25, r25, 1
		}
	}


	// rlwinm r24, r23, 0, 24, 31 (???)
	r25_counter4 = 0; // li r25, 0
	while (r25_counter4 < r24_counter1) { // cmpw r25, r24; blt+ 0x80596730
		res = func_802aefb8(gci_data, total_obfuscated, 2);
		//addi r0, r3, 1
		r25_counter4++; // addi r25, r25, 1
		//stb r0, 0x0038 (r19=803f39b8)
		//addi r19, r19, 1
	}

	if (r20_counter2 >= 5) { //clmpwi r20, 5; blt- 0x8059677c
		res = func_802aefb8(gci_data, total_obfuscated, 20);
	}

	//...
	// blr

/* ------------------------------------------------------------------------- */


/* A lot of different other things happen here (we go up in the call stack)
 * that may or may not be relevant. Eventually we enter func_80596810 below.
 * This function seems like it's responsible for actually building the replay
 * array that encodes some inputs. */


/* -------- Function 0x80596810 00_Do_Decompression1? ---------------------- */

	res = func_802aefb8(gci_data, total_obfuscated, 8);

	r20_counter7 = 0;// li r20, 0
	r4_off_0x0110 = (uint16_t)res; //sth r3, -0x0110(r4=81291380)
	r23_counter8 = 0;  //li r23, 0

	while (r20_counter7 < r4_off_0x0110) { //cmpw r20, r0; blt+ 0x805968cc
		res = func_802aefb8(gci_data, total_obfuscated, 14);
		res = func_802aefb8(gci_data, total_obfuscated, 14);
		res = func_802aefb8(gci_data, total_obfuscated, 4);
		res = func_802aefb8(gci_data, total_obfuscated, 5);
		res = func_802aefb8(gci_data, total_obfuscated, 5);
		res = func_802aefb8(gci_data, total_obfuscated, 5);
		res = func_802aefb8(gci_data, total_obfuscated, 5);
		res = func_802aefb8(gci_data, total_obfuscated, 5);

		r19_counter9 = 0; // li r19, 0
		// li r24, 0 (???)
		// ...

		r21_counter9 = 1; // lbz r0, 0 (r21) (don't know where this is from)
		while (r19_counter9 < r21_counter9) { //cmpw r19, r0; blt+ 0x80596a18
			res = func_802aefb8(gci_data, total_obfuscated, 32);
			res = func_802aefb8(gci_data, total_obfuscated, 32);
			res = func_802aefb8(gci_data, total_obfuscated, 32);
			res = func_802aefb8(gci_data, total_obfuscated, 32);
			res = func_802aefb8(gci_data, total_obfuscated, 32);
			res = func_802aefb8(gci_data, total_obfuscated, 32);
			r19_counter9++;
		}

		res = func_802aefb8(gci_data, total_obfuscated, 32);
		res = func_802aefb8(gci_data, total_obfuscated, 32);
		res = func_802aefb8(gci_data, total_obfuscated, 32);
		res = func_802aefb8(gci_data, total_obfuscated, 32);
		res = func_802aefb8(gci_data, total_obfuscated, 32);
		res = func_802aefb8(gci_data, total_obfuscated, 32);
		r20_counter7++;
	}

	// This call returns the number of entries in the decompressed replay array
	replay_array_length = func_802aefb8(gci_data, total_obfuscated, 14);

	current_array_index = 0x00000000;
	struct replay_entry replay_array[replay_array_length+0x10];
	memset(&replay_array, 0x00, sizeof(replay_array));

	printf("-------------------- replay array --------------------\n");
	while (current_array_index <= replay_array_length){
		replay_array[current_array_index].mask    = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].strafe  = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].accel   = func_802aefb8(gci_data, total_obfuscated, 7);
		replay_array[current_array_index].brake   = func_802aefb8(gci_data, total_obfuscated, 7);
		replay_array[current_array_index].frames  = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].steer_x = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].steer_y = func_802aefb8(gci_data, total_obfuscated, 8);

		current_array_index = current_array_index + 1;
		replay_bytes_counter = replay_bytes_counter + 7;
	}
	// func_802af210();
	// ...
	// Seems like decompression ends here, then the replay starts.

/* ------------------------------------------------------------------------- */

	out = fopen(OUTPUT_FILE, "wb");
	if (fp == NULL)
		exit(-1);
	fwrite(&replay_array, sizeof(replay_array), 1, out);
	fclose(out);

	free(gci_data);
	free(total_obfuscated);
}
