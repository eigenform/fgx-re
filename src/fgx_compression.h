#include <stdint.h>

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

uint32_t decompress(void *compressed_base, uint32_t *total_iterations,
		uint32_t num_iterations);
void decompress_header(unsigned char *gci_data, uint32_t *num_bits);
struct replay_entry *decompress_array(unsigned char *gci_data,
		uint32_t *num_bits, uint32_t *replay_array_length);
