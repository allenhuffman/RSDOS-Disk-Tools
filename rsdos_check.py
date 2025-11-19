def print_fat(fat):
    print("FAT Table:")
    for i in range(0, len(fat), 16):
        chunk = fat[i:i+16]
        hex_bytes = ' '.join(f"{b:02X}" for b in chunk)
        print(f"{i:02X}: {hex_bytes}")

#!/usr/bin/env python3
"""
rsdos_check.py - Check RS-DOS disk image for errors and inconsistencies

Usage:
  python rsdos_check.py <disk.dsk>

Checks performed:
- Directory entry validity
- Granule chain loops and out-of-bounds
- Orphaned granules (not used by any file)
- Multiple files sharing granules
- Free granule count
"""
import sys

DIR_START = 79104   # Track 17, sector 3
DIR_SIZE = 2304     # 9 sectors * 256 bytes
ENTRY_SIZE = 32     # Directory entry size
NUM_ENTRIES = 72    # 9 sectors * 8 entries
FAT_START = 78848   # Track 17, sector 2
FAT_SIZE = 68       # 68 granules


def get_fat(data):
    fat_offset = 17 * 18 * 256 + (2 - 1) * 256  # 78848
    return bytearray(data[fat_offset:fat_offset + 68])

def read_directory(data):
    entries = []
    # Directory is on track 17, sectors 3-11 (offsets 79104-81408)
    for sector in range(3, 12):  # sectors 3-11
        sector_offset = 17 * 18 * 256 + (sector - 1) * 256
        sector_data = data[sector_offset:sector_offset + 256]
        for e in range(8):  # 8 entries per sector
            entry = sector_data[e * 32:(e + 1) * 32]
            if entry[0] == 255:
                return entries  # End of directory
            entries.append(entry)
    return entries

def is_valid_entry(entry, idx):
    name = entry[0:8].decode('ascii', errors='ignore').rstrip()
    ext = entry[8:11].decode('ascii', errors='ignore').rstrip()
    first_gran = entry[13]
    bytes_last = entry[14] * 256 + entry[15]
    print(f"Entry {idx}: name='{name}', ext='{ext}', first_gran={first_gran}, bytes_last={bytes_last}, raw0={entry[0]}")
    if entry[0] == 255:
        print("  Skipped: end-of-directory marker.")
        return False
    if entry[0] == 0:
        print("  Skipped: deleted file.")
        return False
    print("  Accepted as valid file entry.")
    return True

def get_file_granule_chain(fat, first_gran):
    chain = []
    gn = first_gran
    visited = set()
    max_chain = FAT_SIZE
    while True:
        if gn > 67 or gn < 0:
            print(f"  Chain break: granule {gn} out of bounds.")
            break
        if gn in visited:
            print(f"  Chain break: loop detected at granule {gn}.")
            break
        chain.append(gn)
        visited.add(gn)
        if len(chain) > max_chain:
            print(f"  Chain break: chain too long (> {max_chain} granules).")
            break
        gv = fat[gn]
        if gv == 0:
            # RS-DOS: FAT value 0 means end of file, only bytes_last used
            break
        if gv >= 192:
            # RS-DOS end-of-chain marker; do not follow to next granule
            break
        gn = gv
    return chain

def main():
    if len(sys.argv) < 2:
        print("Usage: python rsdos_check.py <disk.dsk>")
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, 'rb') as f:
        data = f.read()
    fat = get_fat(data)
    print_fat(fat)
    print()
    entries = read_directory(data)
    print(f"Checking {filename}...")
    granule_usage = [0]*FAT_SIZE
    file_count = 0
    for idx, entry in enumerate(entries):
        if not is_valid_entry(entry, idx):
            continue
        file_count += 1
        name = entry[0:8].decode('ascii', errors='ignore').rstrip()
        chain = get_file_granule_chain(fat, entry[13])
        print(f"{name}: {chain}")
        # Mark granules as used
        for g in chain:
            granule_usage[g] += 1
        # ...existing code...
    # Check for orphaned and multiply-used granules
    orphaned = [i for i in range(FAT_SIZE) if fat[i] != 255 and granule_usage[i] == 0]
    multiply_used = [i for i, u in enumerate(granule_usage) if u > 1]
    free_granules = [i for i in range(FAT_SIZE) if fat[i] == 255]
    used_granules = [i for i, u in enumerate(granule_usage) if u > 0]
    print(f"\nSummary:")
    print(f"  Files found: {file_count}")
    print(f"  Used granules: {len(used_granules)}")
    print(f"  Free granules: {len(free_granules)}")
    print(f"  Orphaned granules: {orphaned}")
    print(f"  Multiply-used granules: {multiply_used}")
    print(f"  Total granules: {FAT_SIZE}")
    print(f"  Granule usage: {granule_usage}")

if __name__ == "__main__":
    main()
