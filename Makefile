all:
	gcc src/fgx-deflate-replay/*.c -o fgx-deflate-replay
	gcc src/fgx-checksum/*.c -o fgx-checksum
clean:
	rm -v fgx-deflate-replay fgx-checksum
