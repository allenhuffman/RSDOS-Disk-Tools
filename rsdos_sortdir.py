#!/usr/bin/env python3
"""
rsdos_sortdir.py - Sort RS-DOS directory entries alphabetically in a disk image

Usage:
  python rsdos_sortdir.py <disk.dsk> [--output <new.dsk>] [--inplace]

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
    entries = []
    # Track 17, sectors 3-11
    for sector in range(3, 12):
        sector_offset = 17 * 18 * 256 + (sector - 1) * 256
        sector_data = data[sector_offset:sector_offset + 256]
        for e in range(8):
            entry = sector_data[e * 32:(e + 1) * 32]
            if entry[0] == 255:
                return entries  # End of directory
            if entry[0] == 0:
                continue  # Deleted file
            entries.append(entry)
    return entries


def is_valid_entry(entry):
    return entry[0] not in (0, 255)


def entry_key(entry):
    name = entry[0:8].decode('ascii', errors='ignore').rstrip()
    ext = entry[8:11].decode('ascii', errors='ignore').rstrip()
    return (name, ext)


def sort_directory(entries):
    # All entries are valid (already filtered in read_directory)
    return sorted(entries, key=entry_key)


def write_directory(data, sorted_entries):
    # Write sorted entries back, pad with unused entries (0xFF)
    dir_bytes = b''.join(sorted_entries)
    unused_count = NUM_ENTRIES - len(sorted_entries)
    if unused_count > 0:
        dir_bytes += bytes([255] + [0]*31) * unused_count
    data = bytearray(data)
    data[DIR_START:DIR_START + DIR_SIZE] = dir_bytes
    return data


def show_directory(entries, title):
    print(title)
    print("#   FILENAME EXT")
    print("----------------")
    for idx, entry in enumerate(entries):
        name = entry[0:8].decode('ascii', errors='ignore').rstrip()
        ext = entry[8:11].decode('ascii', errors='ignore').rstrip()
        print(f"{idx:02d}  {name:<8} {ext:<3}")
    print(f"\nTotal entries: {len(entries)}")


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

    show_directory(entries, "Directory Entries (Pre-Sort):")
    show_directory(sorted_entries, "\nDirectory Entries (Sorted):")

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
