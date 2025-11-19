# Disk Extended Color BASIC Disk Image Parser

This repository contains a simple Python script to parse Disk Extended Color BASIC disk images for the TRS-80 Color Computer and display a directory listing.

## Script: rsdos_dir.py

Parses the directory from an RS-DOS .DSK file and lists files with their names, types, and sizes.

### Usage

```bash
python3 rsdos_dir.py <disk.dsk>
```

Replace `<disk.dsk>` with the path to your RS-DOS disk image file.

### Requirements

- Python 3.x

### Example Output

```
Directory listing:
----------------------------------------
PEN-PAL  BAS 0 B     69120 bytes
ONERROR  BAS 0 B     29952 bytes
TELETAPE BIN 2 B    119808 bytes
TELETERM BIN 2 B     32256 bytes
PAPER    BAS 0 B     64512 bytes
PAPER+   BAS 0 B    122112 bytes
WNDO     BAS 0 B    126720 bytes
GETERM   BIN 2 B     13824 bytes
MODMSCAN BAS 0 B     25344 bytes
CONVERT  BAS 0 B     23040 bytes
GETC10   BIN 2 B     73728 bytes
WNDO11   BAS 0 B     87552 bytes
PATCH    BAS 0 B     85248 bytes
SONG          1 A      2304 bytes
BIQUOTES XXX 1 A      2304 bytes
AFFAIR        1 A      2304 bytes
KASMSG        1 A      2304 bytes
SCHEDULE OLD 0 B     82944 bytes
BANNER   BAS 0 B     96768 bytes
MATRIX        1 A      4608 bytes
SENDISK  BIN 2 B         0 bytes
TOP CAT       1 A      2304 bytes
RICHARD       1 A      2304 bytes
MSCAN 11 BAS 0 B     89856 bytes
C        BAS 0 B     41472 bytes
DTR22    BIN 2 B    110592 bytes
SCHEDULE BAS 0 B     92160 bytes
WELCOME  TXT 1 A      2304 bytes
SCHEDULE BEC 0 B     94464 bytes
FINISH   BAS 0 B     57600 bytes
```

### Notes

- Assumes standard Disk Extended Color BASIC format: 35 tracks (or 40 with patch), 18 sectors/track, single-sided, 256 bytes/sector.
- Directory is read from track 17, sectors 3-11.
- Only lists valid (non-deleted) entries.
- Size calculation is based on allocated granules and sectors.

# RSDOS-Disk-Tools

A collection of Python utilities for parsing, analyzing, and manipulating RS-DOS disk images for the TRS-80 Color Computer.

## Features
- Directory listing with file sizes, types, ASCII/BIN flags
- FAT table display
- Granule chain display for each file
- Free space and unused space calculation
- Extensible for future RS-DOS disk utilities

## Usage
```
python rsdos_dir.py [--fat] [--granules] <disk.dsk>
```

- `--fat`      Show FAT table
- `--granules` Show granule chain for each file

## Example Output
```
FAT Table:
00: FF FF 03 C1 05 02 07 04 09 06 0B 08 C1 0A 0F 0C
10: 11 0E 13 10 15 12 17 14 19 16 C6 18 1D 1A 1F C7
20: C1 22 C1 C9 25 26 C2 28 29 2A 2B 2C 2D C5 C1 30
30: C8 C1 33 C2 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40
40: 41 42 43 0D

FILENAME EXT TYPE T   SIZE  GRANULES
------------------------------------
1        TXT BDAT B      1  32
2304     TXT BDAT B   2304  33,34
2303     TXT BDAT B   2303  35
4000     TXT BDAT B   4000  30,31
5000     TXT BDAT B   5000  36,37,38
6000     TXT BDAT B   6000  28,29,26
15000    TXT BDAT B  15000  39,40,41,42,43,44,45
30000    TXT BDAT B  30000  27,24,25,22,23,20,21,18,19,16,17,14,15,12
42       TXT BDAT B     42  46
4242     TXT BDAT B   4242  47,48
MAKEFILE BAS BPRG B    211  49
FILEINFO BAS BPRG B   2751  50,51
60000    TXT BDAT B  60000  52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,13,10,11,8,9,6,7,4,5,2,3

Free space: 2 granules (4608 bytes)
Unused space (lost to granule rounding, etc): 20210 bytes
```

## Future Plans
- Disk image editing
- File extraction/insertion
- Disk integrity checking
- Support for other Color Computer disk formats

## License
MIT