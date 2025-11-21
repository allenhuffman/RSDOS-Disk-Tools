# RS-DOS (DECB, Disk Extended Color BASIC) Disk Structure

Disk Extended Color BASIC supports:

* Single-sided disk
* 35 Tracks (numbers track 0-34)
* 18 Sectors per Track (numbered 1-18)
* Sector size of 256 bytes

Each track would hold 18*256 = 4608 bytes.

## 35 Tracks per Disk
```
+----------+
| Track 00 | - 4608 bytes
+----------+
| Track 01 | - 4608 bytes
+----------+
|    ...   |
|    ...   |
+----------+
| Track 17 | - File Allocation Table and Directory
+----------+
|    ...   |
|    ...   |
+----------+
| Track 33 | - 4608 bytes
+----------+
| Track 34 | - 4608 bytes
+----------+
```

## 18 Sectors per Track
```
Track X
+----+----+----+-----+----+----+----+
| 01 | 02 | 03 | ... | 06 | 07 | 18 | - 256 bytes each
+----+----+----+-----+----+----+----+
```

## Granules

RS-DOS divides the disk up into half-track sized granules (2304 bytes each) numbered 0-67.

Granules 0-33 are on Tracks 0-16.
Track 17 is reserved for FAT and directory and does not contain any granules.
Granules 34-67 are on Tracks 18-34.

Any routines accessing granules need to take this into consideration.

```
Track 00 +------------+
         | Granule 00 | - Sectors 1-9   (2304 bytes)
         | Granule 01 | - Sectors 10-18 (2304 bytes)
Track 01 +------------+
         | Granule 02 | - Sectors 1-9   (2304 bytes)
         | Granule 03 | - Sectors 10-18 (2304 bytes)
Track xx +------------+
         |     ...    |
Track 16 +------------+
         | Granule 32 | - Sectors 1-9   (2304 bytes)
         | Granule 33 | - Sectors 10-18 (2304 bytes)
Track 17 +------------+
         | FAT &      | - 4608 bytes (no granules)
         | Directory  |
Track 18 +------------+
         | Granule 34 | - Sectors 1-9   (2304 bytes)
         | Granule 35 | - Sectors 10-18 (2304 bytes)
Track xx +------------+
         |     ...    |
Track 34 +------------+
         | Granule 66 | - Sectors 1-9   (2304 bytes)
         | Granule 67 | - Sectors 10-18 (2304 bytes)
         +------------+
```

## FAT and Directory

RS-DOS uses Track 17 for the Directory and FAT.

* Sector 1 – Unused (“for future use”)
* Sector 2 – File Allocation Table (FAT)
* Sectors 3-11 – Directory Entries
* Sectors 12-18 – Unused (“for future use”)

### FAT (Sector 2)

The first 68 bytes of Sector 2 contained the file allocation table. Each byte represented the status of one of the available granules on the disk. If the granule was not used by any file, the byte representing it will be set to 255 (0xFF).

If the granule is used, but the file is larger and continues on to another granule, the value will be the granule number for the next granule of the file (1-68).

If the granule is used, but the file does not continue to another granule, the top two bits will be set (11xxxxxx, hex value 0xC0 or decimal 192) and the remaining five bits will indicate how many sectors of that granule are part of the file.

### Directory (Sectors 3-11)

* Bytes 0-7 - Filename, left-justified, blank filled. If byte 0 is 0, the file has been deleted and the entry is available. If byte 0 is 255, the entry and all following entries have not yet been used (end of directory entries).
* Bytes 8-10 - Filename extension, left-justified, blank filled.
* Byte 11 - File type (0=BASIC program, 1=BASIC data file, 2=Machine-language program, 3=Text editor source file)
* Byte 12 - ASCII flag. If byte 12 is 0, the file is in binary format. If byte 12 is 255, the file is in ASCII format.
* Byte 13 - The number of the first granule in the file (0-67).
* Bytes 14-15 - The number of bytes in use in the last sector of the file.
* Bytes 16-31 - Reserved for future use.

## References
* https://colorcomputerarchive.com/repo/Documents/Manuals/Hardware/Color%20Computer%20Disk%20System%20(Tandy).pdf (1981)
* https://colorcomputerarchive.com/repo/Documents/Manuals/Hardware/Color%20Computer%20Disk%20System%20Programming%20Manual%20(Tandy).pdf (1986)

