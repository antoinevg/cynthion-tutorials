/*
 * Automatically generated by luna-soc; edits will be discarded on rebuild.
 * (Most header files phrase this 'Do not edit.'; be warned accordingly.)
 *
 * Generated: 2024-05-23 14:53:14.966491.
 */

MEMORY {
    /* 0x00010000 = 65536 bytes */
    mainram : ORIGIN = 0x00000000, LENGTH = 0x00010000
}

REGION_ALIAS("REGION_TEXT", mainram);
REGION_ALIAS("REGION_RODATA", mainram);
REGION_ALIAS("REGION_DATA", mainram);
REGION_ALIAS("REGION_BSS", mainram);
REGION_ALIAS("REGION_HEAP", mainram);
REGION_ALIAS("REGION_STACK", mainram);
