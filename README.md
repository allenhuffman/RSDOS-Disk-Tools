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