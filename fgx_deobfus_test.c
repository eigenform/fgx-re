#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define TEST_FILE "test_00.bin"

 /* See questions/7775991/how-to-get-hexdump-of-a-structure-data */
void hexdump(char *desc, void *addr, int len)
{
	unsigned char *pc = (unsigned char*)addr;
	unsigned char buff[17];
	int i;

	if (desc != NULL) printf ("%s:\n", desc);
	if (len == 0)
	{
		printf("  ZERO LENGTH\n");
		return;
	}
	if (len < 0)
	{
		printf("  NEGATIVE LENGTH: %i\n",len);
		return;
	}

	for (i = 0; i < len; i++)
	{
		if ((i % 16) == 0)
		{
			if (i != 0)
				printf("  %s\n", buff);
			printf("  %04x ", i);
		}
		
		printf(" %02x", pc[i]);
		if ((pc[i] < 0x20) || (pc[i] > 0x7e))
			buff[i % 16] = '.';
		else
			buff[i % 16] = pc[i];
		buff[(i % 16) + 1] = '\0';
	}

	while ((i % 16) != 0)
	{
		printf("   ");
		i++;
	}
	
	printf("  %s\n", buff);
}


/* Structure of un-obfuscated replay data. From yoshifan's research, which
 * you can find here:
 *
 *	https://github.com/yoshifan/fzerogx-docs
 *
 */
struct replay_entry {
	uint8_t mask;
	int8_t steer_x;
	int8_t steer_y;
	int8_t strafe;
	uint8_t accel;
	uint8_t brake;
	uint8_t frames;
} __attribute__((__packed__));


/* This seems like the function actually responsible for de-obfuscating bytes.
 * It looks like this in Dolphin:
 *
 *	   zz_802aefb8_:
 *	   802aefb8: li		r8, 0
 *	   802aefbc: li		r7, 1
 *	   802aefc0: mtctr	r5
 *	   802aefc4: cmplwi	r5, 0
 *	   802aefc8: beq-	 ->0x802AF008
 *	   802aefcc: lwz	r6, 0 (r4)
 *	   802aefd0: rlwinm	r0, r6, 29, 3, 31 (fffffff8)
 *	   802aefd4: rlwinm	r6, r6, 0, 29, 31 (00000007)
 *	   802aefd8: lbzx	r0, r3, r0
 *	   802aefdc: slw	r6, r7, r6
 *	   802aefe0: and.	r0, r6, r0
 *	   802aefe4: beq-	 ->0x802AEFF4
 *	   802aefe8: subi	r0, r5, 1
 *	   802aefec: slw	r0, r7, r0
 *	   802aeff0: or		r8, r8, r0
 *	   802aeff4: lwz	r6, 0 (r4)
 *	   802aeff8: subi	r5, r5, 1
 *	   802aeffc: addi	r0, r6, 1
 *	   802af000: stw	r0, 0 (r4)
 *	   802af004: bdnz+	 ->0x802AEFCC
 *	   802af008: mr		r3, r8
 *	   802af00c: blr	
 */
uint32_t func_802aefb8(void *compressed_base, uint32_t *total_iterations,
		uint32_t num_iterations) {

	uint32_t result = 0;
	int ctr = num_iterations;
	uint32_t base_offset;
	uint32_t mask;
	uint32_t input_val;
	void *input_ptr;

	if (num_iterations == 0)
		goto loc_802af008; // this will probably never be the case

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

loc_802af008:
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
 * representation of this whole process. Some of the loop counters here may
 * be particular to/computed specifically for handling the input from
 * 8P-GFZE-fzr000035804D31D70EE97E77 in particular.
 *
 * Note that, in the actual code, we always `li r5, <some number` for passing
 * the `num_iterations` argument to func_802aefb8 (so at least these
 * function calls are correct in that sense).
 */
int main() {
	uint32_t result;
	uint32_t *total_obfuscated = malloc(sizeof(uint32_t));
	*total_obfuscated = 0x00;

	unsigned char *gci_data = malloc(0x4000);
	FILE *fp = fopen(TEST_FILE, "rb");
	if (fp == NULL)
		exit(-1);
	fread(gci_data, 0x4000,1,fp);

	/* When PC=0x80596450 */
loc_80596450:
	result = func_802aefb8(gci_data, total_obfuscated, 8);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 7);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 6);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 3);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 2);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 1);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 7);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	/* We jump somewhere else here (function call i think)...
	 * .
	 * .
	 * .
	 */

	result = func_802aefb8(gci_data, total_obfuscated, 1);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 6);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	/* some loop here where initially r20=5, and we `cmplwi r20, 3`,
	 * otherwise blt- 0x80596574 */

	int some_counter = 5;
	if (some_counter == 3)
		goto loc_80596574;

loc_80596560:
	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	if (some_counter == 2)
		goto loc_80596590;

	result = func_802aefb8(gci_data, total_obfuscated, 7);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	// The byte at 0x8039b560 is compared against 0x00
	// (initially it's 0x01); dunno what this is
	uint8_t unk_byte1 = 0x01;
	if (unk_byte1 == 0x00)
		goto loc_805966b4;
	
	result = func_802aefb8(gci_data, total_obfuscated, 2);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	if (some_counter > 2)
		goto loc_805965cc;


loc_80596574:
loc_80596590:
loc_805965cc:
	// Some stuff happens here that I don't understand
	//  . . .
	result = func_802aefb8(gci_data, total_obfuscated, 1);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	// We always pass over this branch for this specific file.
	// This may not always be the case.
	// rlwinm. r0, result, 0, 24, 31
	// beq- 0x8059665c

loc_8059665c:
	// do some things
	// bl 80008bec
loc_805966b4:

loc_80596700:
	result = func_802aefb8(gci_data, total_obfuscated, 1);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);


loc_80596730:
	result = func_802aefb8(gci_data, total_obfuscated, 2);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	if (some_counter < 5)
		goto loc_8059677c;

	result = func_802aefb8(gci_data, total_obfuscated, 20);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);


loc_8059677c:

loc_80596810:

loc_80596844:
	result = func_802aefb8(gci_data, total_obfuscated, 8);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

loc_805968cc:
loc_805968d8:
	result = func_802aefb8(gci_data, total_obfuscated, 14);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 14);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 4);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);


loc_80596a18:
	/* This block is a loop over some value in r20, dunno.
	 * For this GCI, it just runs once  */
	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);


loc_80596ba0:
	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf(" result: 0x%08x\n", result);
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);


	int some_counter_2;
	some_counter_2++;
	if (some_counter_2 < 4)
		goto loc_805968cc;

loc_80596d18:
	result = func_802aefb8(gci_data, total_obfuscated, 14);
	printf(" result: 0x%08x\n", result);
	// the "count" here of total_obfuscated should be 0x78e
	printf("\ttotal_obfuscated: 0x%08x\n", *total_obfuscated);

//loc_80596e1c:
	uint32_t current_array_index;
	current_array_index = 0x00000000;
	uint32_t replay_array_length; // should be 0x000007c7 for this GCI
	uint32_t replay_bytes_counter;
	replay_array_length = result;

	struct replay_entry replay_array[replay_array_length+0x10];
	memset(&replay_array, 0x00, sizeof(replay_array));

	while (current_array_index <= replay_array_length){

		result = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].mask = result;

		result = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].strafe = result;

		result = func_802aefb8(gci_data, total_obfuscated, 7);
		replay_array[current_array_index].accel = result;

		result = func_802aefb8(gci_data, total_obfuscated, 7);
		replay_array[current_array_index].brake = result;

		result = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].frames = result;

		result = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].steer_x = result;

		result = func_802aefb8(gci_data, total_obfuscated, 8);
		replay_array[current_array_index].steer_y = result;

		current_array_index = current_array_index + 1;
		replay_bytes_counter = replay_bytes_counter + 7;
	}
	hexdump("computed array", &replay_array, sizeof(replay_array));

	free(gci_data);
	free(total_obfuscated);
}
