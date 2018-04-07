all:
	gcc src/fgx-decompress-replay.c src/fgx_compression.c -o fgx-decompress-replay
	gcc src/fgx-checksum.c -o fgx-checksum
clean:
	rm -v fgx-decompress-replay fgx-checksum
