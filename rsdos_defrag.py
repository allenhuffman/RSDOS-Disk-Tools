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


def get_fat(data):
    return bytearray(data[FAT_START:FAT_START+FAT_SIZE])

def set_fat(data, fat):
    data = bytearray(data)
    data[FAT_START:FAT_START+FAT_SIZE] = fat
    return data

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

def write_directory(data, entries):
    dir_bytes = b''.join(entries)
    data = bytearray(data)
    data[DIR_START:DIR_START + DIR_SIZE] = dir_bytes
    return data

def is_valid_entry(entry):
    return entry[0] not in (0, 255)

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
            break
        gn = gv
    return chain

def defrag_disk(data):
    data = bytearray(data)
    fat = get_fat(data)
    entries = read_directory(data)
    used_granules = set()
    file_infos = []
    print(f"Found {len(entries)} directory entries.")
    # Gather file info and data
    for idx, entry in enumerate(entries):
        if not is_valid_entry(entry):
            continue
        first_gran = entry[13]
        chain = get_file_granule_chain(fat, first_gran)
        print(f"Entry {idx}: first granule {first_gran}, chain {chain}")
        file_data = bytearray()
        for g in chain:
            if g < 0 or g >= FAT_SIZE:
                print(f"Warning: granule {g} out of bounds for file at entry {idx}")
                break
            file_data += data[g*2304:(g+1)*2304]
        file_infos.append((idx, entry, chain, file_data))
        used_granules.update(chain)
    print(f"Total files to defrag: {len(file_infos)}")
    # Defrag: assign contiguous granules to each file
    all_granules = list(range(FAT_SIZE))
    free_granules = [g for g in all_granules if fat[g] == 255]
    print(f"Free granules before defrag: {free_granules}")
    next_gran = 0
    new_fat = bytearray([255]*FAT_SIZE)
    new_entries = list(entries)
    for idx, entry, chain, file_data in file_infos:
        needed = len(chain)
        print(f"Defragging entry {idx}: needs {needed} granules, assigning from {next_gran} to {next_gran+needed-1}")
        if next_gran + needed > FAT_SIZE:
            print(f"Error: Not enough free granules to defrag file at entry {idx}")
            break
        # Find next contiguous block of free granules
        while next_gran < FAT_SIZE and new_fat[next_gran] != 255:
            next_gran += 1
        start = next_gran
        new_chain = list(range(start, start+needed))
        # Write file data to new granules
        bytes_last = entry[14] * 256 + entry[15]
        for i, g in enumerate(new_chain):
            if g >= FAT_SIZE:
                print(f"Error: granule {g} out of bounds during write for file at entry {idx}")
                break
            if i < needed-1:
                data[g*2304:(g+1)*2304] = file_data[i*2304:(i+1)*2304]
                new_fat[g] = new_chain[i+1]
            else:
                # Last granule
                last_fat_val = fat[chain[-1]]
                if last_fat_val == 0:
                    # Only bytes_last used
                    data[g*2304:(g*2304)+bytes_last] = file_data[i*2304:(i*2304)+bytes_last]
                    # Zero out the rest of the granule
                    data[(g*2304)+bytes_last:(g+1)*2304] = b'\x00' * (2304 - bytes_last)
                    new_fat[g] = 0
                else:
                    data[g*2304:(g+1)*2304] = file_data[i*2304:(i+1)*2304]
                    new_fat[g] = last_fat_val # preserve last granule value
        # Update entry with new first granule
        new_entry = bytearray(entry)
        new_entry[13] = new_chain[0]
        new_entries[idx] = bytes(new_entry)
        next_gran += needed
        print(f"Entry {idx} defragged: new chain {new_chain}")
    # Update FAT and directory
    data = set_fat(data, new_fat)
    data = write_directory(data, new_entries)
    print("Defrag complete.")
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
