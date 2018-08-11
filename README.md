# fgx-re
Tools and code for understanding F-Zero GX internals. Includes tools for
preparing save files with the `strcpy()` exploit we found for SGDQ2018, and
also includes an example of a loader for booting DOL files from memory card.

## Python Tools
You can import the `py/fgx_format.py` and `py/fgx_encode.py` scripts in order
to have some interfaces for manipulating F-Zero GX save files in Python.
Read some of the other scripts in `py/` for example usage.

## The garage-data `strcpy()` exploit
If you're interested in the mechanics of the `strcpy()` exploit, have a read
through `py/prepare-ace.py`.

## Building the example DOL loader
You'll have to drop in a valid F-Zero GX garage data file into this directory
first, and then set the `BASE_GCI` variable in `dol-loader/Makefile`.
Then, you should just have to run `make` (note that you'll also have to have
`devkitPPC` installed -- the current `Makefile` assumes that the
`powerpc-eabi-{objcopy,ld,gcc}` binaries are already in your `$PATH`).
