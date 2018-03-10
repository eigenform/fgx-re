#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define TEST_FILE "test_00.bin"

// rlwinm does a circular rotate left, then logical AND against some mask
uint32_t rlwinm(uint32_t val, uint32_t shl, uint32_t mask) {
    return ( (val << shl) | ((val >> (32 - shl)) & ~(-1 << shl))) & mask;
}

uint32_t shl(uint32_t val, uint32_t shl){
    return (val << shl) | ((val >> (32 - shl)) & ~(-1 << shl));
}


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
		//printf("\ttotal_iterations: %x\n", *total_iterations);

		/* This started half-working when I negate this mask (???) */
		base_offset = rlwinm(*total_iterations, 29, ~0xfffffff8);

		input_ptr = compressed_base + base_offset;
		//printf("\tbase: %p, offset: %x\n", compressed_base, base_offset);
		input_val = *(uint8_t*)input_ptr;
		//printf("\tinput_val: %x\n", input_val);

		mask = rlwinm(*total_iterations, 0, 0x00000007);
		mask = 1 << (mask & 0x1F); // Up to 16 bits of left-shift
		//printf("\tmask: %x\n", mask);

		if (mask & input_val) {
			//r0 = 1 << ((num_iterations - 1) & 0x1F);
			//result = result | r0;
			result = result | (1 << ((num_iterations -1) & 0x1F));
			//printf("\tresult: %x\n", result);
		}
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
 * I *think* these arguments and expected results are correct.
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

	result = func_802aefb8(gci_data, total_obfuscated, 8);
	printf("expected: 0x00000091, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 7);
	printf("expected: 0x00000005, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 6);
	printf("expected: 0x00000024, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf("expected: 0x496cfc59, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 32);
	printf("expected: 0xcae80767, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 5);
	printf("expected: 0x00000001, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 3);
	printf("expected: 0x00000000, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 2);
	printf("expected: 0x00000002, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 1);
	printf("expected: 0x00000000, result: 0x%08x\n", result);

	result = func_802aefb8(gci_data, total_obfuscated, 7);
	printf("expected: 0x00000003, result: 0x%08x\n", result);


	free(gci_data);
	free(total_obfuscated);
}
