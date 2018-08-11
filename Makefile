all:
	make -C dol-loader/

.PHONY: clean
clean:
	make -C dol-loader/ clean
	@rm -f fgx-dol-loader.gci
