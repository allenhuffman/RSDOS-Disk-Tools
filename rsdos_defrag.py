#!/usr/bin/env python3
"""
rsdos_defrag.py - Defragment RS-DOS disk image granules

Usage:
  python rsdos_defrag.py <disk.dsk> [--output <defragged.dsk>] [--inplace]

Options:
  --output <defragged.dsk>   Write defragmented disk image to a new file
  --inplace                  Update the original disk image in place (backup created)

By default, if neither option is given, the script will print a warning and do nothing.
"""
import sys
import argparse
import shutil

# Placeholder constants for RS-DOS disk layout
DIR_START = 79104   # Track 17, sector 3
DIR_SIZE = 2304     # 9 sectors * 256 bytes
ENTRY_SIZE = 32     # Directory entry size
NUM_ENTRIES = 72    # 9 sectors * 8 entries
FAT_START = 78848   # Track 17, sector 2
FAT_SIZE = 68       # 68 granules


def defrag_disk(data):
    # TODO: Implement defragmentation logic
    # For now, just return the data unchanged
    print("Defrag operation not yet implemented.")
    return data


def main():
    parser = argparse.ArgumentParser(description="Defragment RS-DOS disk image granules.")
    parser.add_argument("disk", help="Disk image file (.dsk)")
    parser.add_argument("--output", help="Write defragmented disk image to a new file")
    parser.add_argument("--inplace", action="store_true", help="Update the original disk image in place (backup created)")
    args = parser.parse_args()

    with open(args.disk, 'rb') as f:
        data = f.read()

    out_data = defrag_disk(data)

    if args.output:
        with open(args.output, 'wb') as f:
            f.write(out_data)
        print(f"Defragmented disk written to {args.output}")
    elif args.inplace:
        backup = args.disk + ".bak"
        shutil.copy2(args.disk, backup)
        with open(args.disk, 'wb') as f:
            f.write(out_data)
        print(f"Defragmented disk written in place. Backup saved as {backup}")
    else:
        print("No action taken. Use --output <defragged.dsk> or --inplace.")

if __name__ == "__main__":
    main()
