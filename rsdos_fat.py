#!/usr/bin/env python3
"""
rsdos_fat.py - Print numbered file list and FAT table with file mapping for RS-DOS disk images

Usage:
  python rsdos_fat.py <disk.dsk>

Features:
- Prints a numbered list of files found in the directory
- Prints the FAT table, showing for each granule the file number it belongs to (or '-' for free/unassigned)
"""
import sys

def get_fat(data):
    # Track is 0-based, sector is 1-based
    fat_offset = (17 * 18 + (2 - 1)) * 256  # Track 17 (0-based), sector 2 (1-based)
    return bytearray(data[fat_offset:fat_offset + 68])

def read_directory(data):
    entries = []
    for sector in range(3, 12):  # sectors 3-11
        sector_offset = 17 * 18 * 256 + (sector - 1) * 256
        sector_data = data[sector_offset:sector_offset + 256]
        for e in range(8):  # 8 entries per sector
            entry = sector_data[e * 32:(e + 1) * 32]
            if entry[0] == 255:
                return entries  # End of directory
            if entry[0] == 0:
                continue  # Deleted file
            entries.append(entry)
    return entries

def get_file_granule_chain(fat, first_gran):
    chain = []
    gn = first_gran
    max_chain = 68
    while True:
        if gn > 67 or gn < 0:
            break
        chain.append(gn)
        gv = fat[gn]
        if gv >= 192:
            break
        gn = gv
        if len(chain) > max_chain:
            break
    return chain

def print_fat_debug(fat):
    for i in range(0, 68, 16):
        row = []
        for j in range(i, min(i+16, 68)):
            row.append(f"{fat[j]:02X}")
        print(f"{i:02X}: {' '.join(row)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python rsdos_fat.py <disk.dsk>")
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, 'rb') as f:
        data = f.read()
    # Track is 0-based, sector is 1-based
    fat_offset = (17 * 18 + (2 - 1)) * 256  # Track 17 (0-based), sector 2 (1-based)
    fat = get_fat(data)
    print("FAT Table (hex values):")
    print_fat_debug(fat)
    print()  # Blank line for readability
    entries = read_directory(data)
    file_gran_map = ['-' for _ in range(68)]
    print("File List:")
    file_list = []
    for idx, entry in enumerate(entries):
        name = entry[0:8].decode('ascii', errors='ignore').rstrip()
        ext = entry[8:11].decode('ascii', errors='ignore').rstrip()
        file_list.append(f"{idx+1}. {name}.{ext}")
        chain = get_file_granule_chain(fat, entry[13])
        for g in chain:
            file_gran_map[g] = str(idx+1)
    for line in file_list:
        print(line)
    print("\nFAT Table (granule #: file #):")
    for i in range(0, 68, 16):
        row = []
        for j in range(i, min(i+16, 68)):
            row.append(f"{file_gran_map[j]:>2}")
        print(f"{i:02X}: {' '.join(row)}")

if __name__ == "__main__":
    main()
