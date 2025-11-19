#!/usr/bin/env python3
"""
rsdos_dirsort.py - Sort RS-DOS directory entries alphabetically in a disk image

Usage:
  python rsdos_dirsort.py <disk.dsk> [--output <new.dsk>] [--inplace]

Options:
  --output <new.dsk>   Write sorted disk image to a new file
  --inplace            Update the original disk image in place

By default, if neither option is given, the script will print a warning and do nothing.
"""
import sys
import argparse
import shutil

DIR_START = 79104   # Track 17, sector 3
DIR_SIZE = 2304     # 9 sectors * 256 bytes
ENTRY_SIZE = 32     # Directory entry size
NUM_ENTRIES = 72    # 9 sectors * 8 entries


def read_directory(data):
    dir_data = data[DIR_START:DIR_START + DIR_SIZE]
    entries = [dir_data[i*ENTRY_SIZE:(i+1)*ENTRY_SIZE] for i in range(NUM_ENTRIES)]
    return entries


def is_valid_entry(entry):
    return entry[0] not in (0, 255)


def entry_key(entry):
    name = entry[0:8].decode('ascii', errors='ignore').rstrip()
    ext = entry[8:11].decode('ascii', errors='ignore').rstrip()
    return (name, ext)


def sort_directory(entries):
    valid = [e for e in entries if is_valid_entry(e)]
    empty = [e for e in entries if not is_valid_entry(e)]
    sorted_valid = sorted(valid, key=entry_key)
    return sorted_valid + empty


def write_directory(data, sorted_entries):
    dir_bytes = b''.join(sorted_entries)
    data = bytearray(data)
    data[DIR_START:DIR_START + DIR_SIZE] = dir_bytes
    return data


def main():
    parser = argparse.ArgumentParser(description="Sort RS-DOS directory entries alphabetically.")
    parser.add_argument("disk", help="Disk image file (.dsk)")
    parser.add_argument("--output", help="Write sorted disk image to a new file")
    parser.add_argument("--inplace", action="store_true", help="Update the original disk image in place")
    args = parser.parse_args()

    with open(args.disk, 'rb') as f:
        data = f.read()

    entries = read_directory(data)
    sorted_entries = sort_directory(entries)

    if args.output:
        out_data = write_directory(data, sorted_entries)
        with open(args.output, 'wb') as f:
            f.write(out_data)
        print(f"Sorted directory written to {args.output}")
    elif args.inplace:
        backup = args.disk + ".bak"
        shutil.copy2(args.disk, backup)
        out_data = write_directory(data, sorted_entries)
        with open(args.disk, 'wb') as f:
            f.write(out_data)
        print(f"Sorted directory written in place. Backup saved as {backup}")
    else:
        print("No action taken. Use --output <new.dsk> or --inplace.")

if __name__ == "__main__":
    main()
