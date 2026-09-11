.include "hdr.asm"

.accu 16
.index 16
.16bit

.SECTION ".cart_hw_text" SUPERFREE

;=============================================================================
; u8 cart_hw_probe(void)
; Checks 24-bit physical address $700000..$700002 for signature 'S', 'H', 0x01
; Returns 1 in tcc__r0 if hardware mailbox detected, 0 otherwise.
;=============================================================================
cart_hw_probe:
    php
    sep #$20            ; 8-bit accumulator
    .accu 8
    lda.l $700000       ; 'S'
    cmp #'S'
    bne @probe_fail
    lda.l $700001       ; 'H'
    cmp #'H'
    bne @probe_fail
    lda.l $700002       ; 0x01
    cmp #$01
    bne @probe_fail

    rep #$20            ; 16-bit accumulator
    .accu 16
    lda #1
    sta.b tcc__r0
    plp
    rtl

@probe_fail:
    rep #$20            ; 16-bit accumulator
    .accu 16
    lda #0
    sta.b tcc__r0
    plp
    rtl

;=============================================================================
; void cart_hw_send_cmd(u8 cmd, u8 index, u8 val)
; Fast 65816 atomic write to RP2350 command mailbox at $7007F0..$7007F3
; Stack layout:
;   1,s..3,s : Return address (PCL, PCH, PB from jsr.l)
;   4,s      : cmd
;   5,s      : index
;   6,s      : val
;=============================================================================
cart_hw_send_cmd:
    php
    sep #$20            ; 8-bit accumulator
    .accu 8
    lda 4,s             ; cmd
    sta.l $7007F0
    lda 5,s             ; index
    sta.l $7007F1
    lda 6,s             ; val
    sta.l $7007F2
    nop
    nop
    lda #$01            ; Handshake flag: SNES request active
    sta.l $7007F3
    rep #$20            ; 16-bit accumulator
    .accu 16
    plp
    rtl

.ENDS
