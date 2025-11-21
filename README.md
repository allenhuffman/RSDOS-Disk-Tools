**NOTE from a Human:**

GitHub Copilot A.I. wrote these scripts. It was an experiment to see if it could figure out the disk format just by searching for information. DO NOT USE except on backups ;-) since this has not really been tested much. The ones that just read (dir, check, fat) should be safe.

---


# RSDOS-Disk-Tools

A collection of Python utilities for parsing, analyzing, and manipulating RS-DOS disk images for the TRS-80 Color Computer.

---

## Features
- Directory listing with file sizes, types, ASCII/BIN flags
- FAT table display
- Granule chain display for each file
- Free space and unused space calculation
- Extensible for future RS-DOS disk utilities


## Running the Scripts

You can run any script in this project in two ways:

**1. Using Python or Python3:**
```
python3 rsdos_dir.py <disk.dsk>
python rsdos_fat.py <disk.dsk>
```
This works on any system with Python installed.

**2. As an Executable (macOS/Linux):**
First, make the script executable:
```
chmod +x rsdos_dir.py rsdos_check.py rsdos_defrag.py rsdos_fat.py rsdos_sortdir.py
```
Then run directly:
```
./rsdos_dir.py <disk.dsk>
./rsdos_fat.py <disk.dsk>
```
This uses the shebang (`#!/usr/bin/env python3`) at the top of each script.

---

## rsdos_dir.py

Parses and displays RS-DOS disk directory listings, file sizes, types, ASCII/BIN flags, FAT table, granule chains, free space, and unused space.

### Usage
```
python rsdos_dir.py [--fat] [--granules] <disk.dsk>
```
- `--fat`      Show FAT table
- `--granules` Show granule chain for each file

### Example Output
```
FAT Table:
00: FF FF 03 C1 05 02 07 04 09 06 0B 08 C1 0A 0F 0C
10: 11 0E 13 10 15 12 17 14 19 16 C6 18 1D 1A 1F C7
20: C1 22 C1 C9 25 26 C2 28 29 2A 2B 2C 2D C5 C1 30
30: C8 C1 33 C2 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40
40: 41 42 43 0D
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
````
---

## rsdos_sortdir.py

Sorts RS-DOS directory entries alphabetically in a disk image.

### Usage
```
python rsdos_sortdir.py <disk.dsk> [--output <new.dsk>] [--inplace]
```
- `--output <new.dsk>`: Write sorted disk image to a new file
- `--inplace`: Update the original disk image in place (backup created)

### Example
```
python rsdos_sortdir.py TEST.DSK --output sorted.dsk
python rsdos_sortdir.py TEST.DSK --inplace
```

---

## rsdos_check.py

Checks RS-DOS disk images for directory and granule chain errors, orphaned granules, multiply-used granules, and provides a summary of disk health.

### Usage
```
python rsdos_check.py <disk.dsk>
```

### Features
- Validates directory entries
- Detects granule chain loops and out-of-bounds errors
- Reports orphaned granules (not used by any file)
- Reports multiply-used granules (shared by more than one file)
- Displays FAT table and per-file granule chains
- Summarizes file count, used/free granules, and errors

### Example Output
```
FAT Table:
00: FF FF 03 C1 05 02 07 04 09 06 0B 08 C1 0A 0F 0C
10: 11 0E 13 10 15 12 17 14 19 16 C6 18 1D 1A 1F C7
20: C1 22 C1 C9 25 26 C2 28 29 2A 2B 2C 2D C5 C1 30
30: C8 C1 33 C2 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40
40: 41 42 43 0D

Checking TEST.DSK...
Entry 0: name='FILE1', ext='TXT', first_gran=32, bytes_last=42, raw0=70
	Accepted as valid file entry.
FILE1: [32]
Entry 1: name='FILE2', ext='TXT', first_gran=33, bytes_last=2304, raw0=70
	Accepted as valid file entry.
FILE2: [33, 34]

Summary:
	Files found: 14
	Used granules: 38
	Free granules: 2
	Orphaned granules: [12, 27]
	Multiply-used granules: [5]
	Total granules: 68
	Granule usage: [0, 1, 1, 1, 1, 2, ...]
```

---

## rsdos_fat.py

Prints a numbered list of files and a FAT table showing which file each granule belongs to. Now uses correct FAT offset logic (track 0-based, sector 1-based), and improved output formatting.

### Usage
```
python rsdos_fat.py <disk.dsk>
```

### Features
- Numbered file list from the directory
- FAT table with each granule showing the file number it belongs to (or '-' for free/unassigned)
- Displays FAT table as hex values for all 68 granules
- Blank line separates FAT output from file list for readability
- FAT offset calculation: Track 17 (0-based), Sector 2 (1-based)

### Example Output
```
FAT Table (hex values):
00: FF FF 03 C1 05 02 07 04 09 06 0B 08 C1 0A 0F 0C
10: 11 0E 13 10 15 12 17 14 19 16 C6 18 1D 1A 1F C7
20: C1 22 C1 C9 25 26 C2 28 29 2A 2B 2C 2D C5 C1 30
30: C8 C1 33 C2 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40
40: 41 42 43 0D

File List:
1. FILE1.TXT
2. FILE2.TXT
3. MAKEFILE.BAS
...

FAT Table (granule #: file #):
00:  -  -  1  2  3  -  4  -  5  -  6  -  7  -  8  -
10:  9  - 10  - 11  - 12  - 13  - 14  - 15  - 16  -
...
```
## rsdos_defrag.py

Defragments RS-DOS disk image granules, making file data contiguous and reducing fragmentation.

### Usage
```
python rsdos_defrag.py <disk.dsk> [--output <defragged.dsk>] [--inplace]
```

### Example
```
python rsdos_defrag.py TEST.DSK --output defragged.dsk
python rsdos_defrag.py TEST.DSK --inplace
```

#### Before
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

#### After

---

## Future Plans
- Disk image editing
- File extraction/insertion
- Disk integrity checking
- Support for other Color Computer disk formats

## License
MIT

---

## Changelog

- **2025-11-20**
    - Updated FAT offset logic in `rsdos_fat.py` (track 0-based, sector 1-based)
    - Improved output formatting: blank line between FAT and file list
    - Removed raw FAT bytes debug output
    - README updated to match actual script names and usage
    - Added instructions for running scripts with `python3` and as executables
