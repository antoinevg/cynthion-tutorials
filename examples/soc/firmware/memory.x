/*
 * Automatically generated by luna-soc; edits will be discarded on rebuild.
 * (Most header files phrase this 'Do not edit.'; be warned accordingly.)
 *
 * Generated: 2024-05-23 14:53:14.966491.
 */

MEMORY {
    /* 0x00010000 = 65536 bytes */
    /*blockram : ORIGIN = 0x00000000, LENGTH = 0x00010000*/
    /*blockram : ORIGIN = 0x00000000, LENGTH = 0x00008000*/
    /*blockram : ORIGIN = 0x00000000, LENGTH = 0x00004000*/
    blockram : ORIGIN = 0x00000000, LENGTH = 0x00002000
    /*blockram : ORIGIN = 0x00000000, LENGTH = 0x00001000*/
    hyperram : ORIGIN = 0x20000000, LENGTH = 0x08000000
}

REGION_ALIAS("REGION_TEXT",   blockram);
REGION_ALIAS("REGION_RODATA", blockram);
REGION_ALIAS("REGION_DATA",   blockram);
REGION_ALIAS("REGION_BSS",    blockram);
REGION_ALIAS("REGION_HEAP",   blockram);
REGION_ALIAS("REGION_STACK",  blockram);
