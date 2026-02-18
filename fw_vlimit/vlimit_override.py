import mmap
import struct
import subprocess

# Define the addresses and instructions
ADDRESS = 0x3fc491e8
OLD_INSTRUCTION = b'\x00\xb0\xe8\x03'  # mov r0, 0x3e8 (1000) in little-endian Videocore encoding
NEW_INSTRUCTION = b'\x00\xb0\xb0\x04'  # mov r0, 0x4b0 (1200) in little-endian Videocore encoding

pagesize = mmap.PAGESIZE  # Adjust as needed

# Open /dev/vc-mem
with open("/dev/vc-mem", "r+b", buffering=0) as f:
    mem = mmap.mmap(f.fileno(), pagesize, offset=ADDRESS & ~(pagesize - 1))

    # Calculate the offset within the mmap region
    offset = ADDRESS % pagesize

    # Read the current instruction (4 bytes)
    current_instruction = mem[offset:offset + 4]

    # Convert byte sequence to integer to compare
    current_int = struct.unpack("<I", current_instruction)[0]
    old_int = struct.unpack("<I", OLD_INSTRUCTION)[0]

    print(f"Current instruction at 0x{ADDRESS:x}: {current_instruction}")

    if current_int == old_int:
        # Replace the instruction
        mem[offset:offset + 4] = NEW_INSTRUCTION
        print(f"Instruction at 0x{ADDRESS:x} replaced.")
    else:
        print(f"Current instruction at 0x{ADDRESS:x} doesn't match expected instruction.")

    mem.close()
    
# Flush the cache using vcgencmd with sudo
try:
    subprocess.run(['sudo', 'vcgencmd', 'cache_flush'], check=True)
    print("Cache flushed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error flushing cache: {e}")
