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
            
            # Filename (8 bytes, ASCII)
            name = entry[0:8].decode('ascii', errors='ignore').rstrip()
            
            # Extension (3 bytes, ASCII)
            ext = entry[8:11].decode('ascii', errors='ignore').rstrip()
            
            # File type (byte 12)
            file_type = entry[11]
            type_strings = {0: 'BPRG', 1: 'BDAT', 2: 'M/L ', 3: 'TEXT'}
            type_str = type_strings.get(file_type, str(file_type))
            
            # ASCII flag (byte 13)
            ascii_flag = entry[12]
            ascii_str = {0:"B", 1:"A"}.get(ascii_flag, str(ascii_flag))

            # First granule (byte 14)
            first_gran = entry[13]
            
            # Bytes used in last sector (bytes 15-16, little endian)
            bytes_last = entry[15] + entry[16] * 256
            
            # Calculate file size in bytes (RS-DOS logic)
            size = 0
            gn = first_gran
            while True:
                if gn > 67 or gn < 0:
                    break  # Invalid granule
                gv = fat[gn]
                if gv < 192:
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
                'size': size
            })
    return entries

def main():
    if len(sys.argv) != 2:
        print("Usage: python rsdos_dir.py <disk.dsk>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Check if file is large enough (minimum disk size for 35 tracks)
    min_size = 35 * 18 * 256  # 161,280 bytes
    if len(data) < min_size:
        print(f"Warning: File size {len(data)} bytes is smaller than expected {min_size} bytes for a 35-track disk.")
    
    # Read FAT (track 17, sector 2, bytes 0-67)
    fat_offset = 17 * 18 * 256 + (2 - 1) * 256  # 78848
    fat = data[fat_offset:fat_offset + 68]
    
    entries = parse_directory(data, fat)
    
    if not entries:
        print("No files found in directory.")
        return
    
    print("FILENAME EXT TYPE T   SIZE")
    print("--------------------------")
    for entry in entries:
        print(f"{entry['name']:<8} {entry['ext']:<3} {entry['type']:<4} {entry['ascii_flag']:<1} {entry['size']:>6}")

if __name__ == "__main__":
    main()

# End of script
# You can now run: python3 rsdos_dir.py TEST.DSK