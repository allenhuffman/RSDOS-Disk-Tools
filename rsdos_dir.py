import os
#!/usr/bin/env python3
"""
Disk Extended Color BASIC Disk Image Directory Parser

This script parses a Disk Extended Color BASIC disk image (.DSK) for the TRS-80 Color Computer
and displays a directory listing with file names, types, and sizes.

Usage: python rsdos_dir.py <disk.dsk>
"""

import sys

def parse_directory(data, fat):
        # All file types use the same calculation: follow FAT chain, add 2304 bytes for each granule, and for the last granule (high two bits set), add (sectors_used-1)*256 + bytes_last from the directory entry.
    """
    Parse the directory from the disk image data.
    Directory is on track 17, sectors 3-11 (offsets 79104-81408).
    """
    dir_start = 79104   # Track 17, sector 3
    dir_size = 2304     # 9 sectors * 256 bytes
    dir_data = data[dir_start:dir_start + dir_size]
    
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
            
            # Filename (bytes 0-7, 8 bytes, ASCII)
            name = entry[0:8].decode('ascii', errors='ignore').rstrip()
            
            # Extension (bytes 8-10, 3 bytes, ASCII)
            ext = entry[8:11].decode('ascii', errors='ignore').rstrip()
            
            # File type (byte 11)
            file_type = entry[11]
            type_strings = {0: 'BPRG', 1: 'BDAT', 2: 'M/L ', 3: 'TEXT'}
            type_str = type_strings.get(file_type, str(file_type))
            
            # ASCII flag (byte 12)
            ascii_flag = entry[12]
            ascii_str = {0:"B", 1:"A"}.get(ascii_flag, str(ascii_flag))

            # First granule (byte 13)
            first_gran = entry[13]
            
            # Bytes used in last sector (bytes 14-15, big endian)
            bytes_last = entry[14] * 256 + entry[15]
            
            # Calculate file size in bytes (RS-DOS logic)
            size = 0
            gn = first_gran
            while True:
                if gn > 67 or gn < 0:
                    break  # Invalid granule
                gv = fat[gn]
                if gv == 0:
                    # Last granule, only bytes_last used
                    size += bytes_last
                    break
                elif gv < 192:
                    size += 2304
                    gn = gv
                else:
                    sectors_used = gv & 0x1F
                    if sectors_used > 0:
                        sectors_used -= 1
                    size += sectors_used * 256 + bytes_last
                    break
            
            entries.append({
                'name': name,
                'ext': ext,
                'type': type_str,
                'ascii_flag': 'A' if ascii_flag == 1 else 'B',
                'size': size,
                'first_gran': first_gran
            })
    return entries

def print_fat(fat):
    print("FAT Table:")
    for i in range(0, len(fat), 16):
        chunk = fat[i:i+16]
        hex_bytes = ' '.join(f"{b:02X}" for b in chunk)
        print(f"{i:02X}: {hex_bytes}")

def get_granule_chain(fat, first_gran):
    chain = []
    gn = first_gran
    while True:
        if gn > 67 or gn < 0:
            break
        chain.append(gn)
        gv = fat[gn]
        if gv >= 192:
            break
        gn = gv
    return chain

def main():
    import argparse
    parser = argparse.ArgumentParser(description="RS-DOS Disk Directory Parser")
    parser.add_argument("disk", nargs="?", help="Disk image file (.dsk)")
    parser.add_argument("--fat", "-f", action="store_true", help="Show FAT table")
    parser.add_argument("--granules", "-g", action="store_true", help="Show granule chain for each file")
    args = parser.parse_args()

    if not args.disk:
        parser.print_help()
        return

    filename = args.disk
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    min_size = 35 * 18 * 256  # 161,280 bytes
    if len(data) < min_size:
        print(f"Warning: File size {len(data)} bytes is smaller than expected {min_size} bytes for a 35-track disk.")

    fat_offset = 17 * 18 * 256 + (2 - 1) * 256  # 78848
    fat = data[fat_offset:fat_offset + 68]

    if args.fat:
        print_fat(fat)
        print()

    entries = parse_directory(data, fat)

    if not entries:
        print("No files found in directory.")
        return

    header = "FILENAME EXT TYPE T   SIZE"
    if args.granules:
        header += "  GRANULES"
    print(header)
    print("-" * len(header))
    for entry in entries:
        line = f"{entry['name']:<8} {entry['ext']:<3} {entry['type']:<4} {entry['ascii_flag']:<1} {entry['size']:>6}"
        if args.granules:
            granule_chain = get_granule_chain(fat, entry['first_gran'])
            line += "  " + ",".join(str(g) for g in granule_chain)
        print(line)

    # Calculate free space
    free_granules = sum(1 for g in fat if g == 255)
    free_bytes = free_granules * 2304
    print(f"\nFree space: {free_granules} granules ({free_bytes} bytes)")

    # Calculate unused space (disk capacity - sum of file sizes - free space)
    disk_capacity = 68 * 2304  # 68 granules per disk
    used_bytes = sum(entry['size'] for entry in entries)
    unused_bytes = disk_capacity - used_bytes - free_bytes
    print(f"Unused space (lost to granule rounding, etc): {unused_bytes} bytes")
if __name__ == "__main__":
    main()