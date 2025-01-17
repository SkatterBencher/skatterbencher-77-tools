import csv
import os
import psutil
import time
import fcntl
import struct

class Measure:
    def __init__(self, command, value=""):
        self.command = command
        self.value = value

class Message:
    __format_string = '6I1028s'
    def __init__(self):
        self.header = [0] * 6
        self.byte_array = bytearray(1028)

    def pack(self):
        return struct.pack(self.__format_string, *self.header, self.byte_array)

    def unpack(self, data):
        unpacked_data = struct.unpack(self.__format_string, data)
        self.header = unpacked_data[:6]
        self.byte_array = unpacked_data[6]

    def get_size(self):
        return struct.calcsize(self.__format_string)

def get_vcgencmd_output(file_desc, command):
    GET_GENCMD_RESULT = 0x00030080
    MAX_STRING = 1024

    p = Message()
    len_cmd = len(command)
    assert len_cmd < MAX_STRING, "vcgencmd command too long"
    p.header[0] = p.get_size()
    p.header[2] = GET_GENCMD_RESULT
    p.header[3] = MAX_STRING
    p.byte_array[:len_cmd] = map(ord, command)
    byte_data = bytearray(p.pack())
    ret_val = fcntl.ioctl(file_desc, 0xC0086400, byte_data)
    if ret_val < 0:
        print(f"ioctl_set_msg failed: {ret_val}")
        return -1
    p.unpack(byte_data)
    return p.byte_array.decode("utf8").rstrip('\x00')

#def get_cpu_usage():
    # Retrieve and return the CPU usage percentage per core
#    return psutil.cpu_percent(interval=1, percpu=True)

def decode_readmr_4(value):
    meanings = {
        "000": "SDRAM low temperature operating limit exceeded",
        "001": "4x refresh",
        "010": "2x refresh",
        "011": "1x refresh (default)",
        "100": "0.5x refresh",
        "101": "0.25x refresh, no derating",
        "110": "0.25x refresh, with derating",
        "111": "SDRAM high temperature operating limit exceeded",
    }
    binary_string = f"{value:03b}" # convert integer in 3-bit binary string
    return meanings.get(binary_string, "Meaning")

def decode_throttling(throttle_hex_value):

    error_messages = {
      0: "UV",
      1: "ArmFreqCap",
      2: "CurThrottle",
      3: "SoftTempLimit",
      16: "UV_occured",
      17: "ArmFreqCap_occured",
      18: "Throttle_occured",
      19: "SoftTempLimit_occured",
    }
    try:
        # Convert hex value to binary string (remove leading '0b')
        binary_value = bin(int(throttle_hex_value, 16))[2:]
    except ValueError:
        return [("Invalid hex value", "N/A")]

    # Invert binary string (active bits are 1s)
    binary_value = binary_value[::-1]

    # Pad binary string with leading zeros to ensure consistent length
    binary_value = binary_value.zfill(20)

    # Initialize empty list for results
    results = []
    for i, message in error_messages.items():
        # Check if index is within binary string length (avoid out-of-range access)
        if i < len(binary_value):
            result = (message, "Yes" if binary_value[i] == "1" else "No")
        else:
            result = (message, "No (bit out of range)")  # Indicate missing bit
        results.append(result)

    return results

def pmic_read_adc(mb):
    # Run the command and capture the output
    output = get_vcgencmd_output(mb, 'pmic_read_adc')
    # Decode byte output to string and split by spaces
    parts = output.strip().split()
    return [(parts[i], parts[i + 1]) for i in range(0, len(parts), 2)]

def main():
    try:
        mb = os.open("/dev/vcio", os.O_RDWR)
    except OSError as e:
        print(f"Can't open device file you need to run this script as root. Error: {e}")
        exit(-1)

    filename = "rpi5_telemetry_fast.csv"
    
    # Generate a timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Append the timestamp to the filename
    base_filename, file_extension = os.path.splitext(filename)
    filename_with_timestamp = f"{base_filename}_{timestamp}{file_extension}"

    fieldnames = [
        "timestamp",
#        "cpu_percent",
        "arm_mhz",
        "core_mhz",
        "v3d_mhz",
        "sdram_mhz",
        "h264_mhz",
        "hevc_mhz",
        "isp_mhz",
        "uart_mhz",
        "pwm_mhz",
        "emmc_mhz",
        "emmc2_mhz",
        "m2mc_mhz",
        "pixel_mhz",
        "pixel_bvb_mhz",
        "vec_mhz",
        "hdmi_mhz",
        "display_mhz",
        "dpi_mhz",
        "arm_temp",
        "core_volt",
        "sdram_c_volt",
        "sdram_i_volt",
        "sdram_p_volt",
        "3V7_WL_SW_A",
        "3V3_SYS_A",
        "1V8_SYS_A",
        "DDR_VDD2_A",
        "DDR_VDDQ_A",
        "1V1_SYS_A",
        "0V8_SW_A",
        "VDD_CORE_A",
        "3V3_DAC_A",
        "3V3_ADC_A",
        "0V8_AON_A",
        "HDMI_A",
        "3V7_WL_SW_V",
        "3V3_SYS_V",
        "1V8_SYS_V",
        "DDR_VDD2_V",
        "DDR_VDDQ_V",
        "1V1_SYS_V",
        "0V8_SW_V",
        "VDD_CORE_V",
        "3V3_DAC_V",
        "3V3_ADC_V",
        "0V8_AON_V",
        "HDMI_V",
        "EXT5V_V",
        "BATT_V",
        "readmr_4",
        "readmr_5",
        "readmr_6",
        "readmr_8",
        "throttle_hex",
        "UV",
        "ArmFreqCap",
        "CurThrottle",
        "SoftTempLimit",
        "UV_occured",
        "ArmFreqCap_occured",
        "Throttle_occured",
        "SoftTempLimit_occured",
        "readosc_1",
        "readosc_2",
        "readosc_3",
        "readosc_4",
        "readosc_5",
        "readosc_6",
        "readosc_7",
        "readosc_8",
        "readosc_9",
        "readosc_10",
        "readosc_11",
        "readosc_12",
        "readosc_13",
        "readosc_14",
        "readosc_15",
        "readosc_16",
        "readosc_17",
        "readosc_18",
        "readosc_19",
        "readosc_20",
        "readosc_21",
        "readosc_22",
        "readosc_23",
        "readosc_24",
        "readosc_25",
        "readosc_26",
        "readosc_27",
        "readosc_28",
        "readosc_29",
        "readosc_30",
        "readosc_31",
        "readosc_32",
        "readosc_33",
    ]

    # Open the file with the new filename
    with open(filename_with_timestamp, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    clocks = {
        "arm": Measure("measure_clock arm"),
        "core": Measure("measure_clock core"),
        "v3d": Measure("measure_clock v3d"),
        "sdram": Measure("measure_clock sdram"),
        "h264": Measure("measure_clock h264"),
        "hevc": Measure("measure_clock hevc"),
        "isp": Measure("measure_clock isp"),
        "uart": Measure("measure_clock uart"),
        "pwm": Measure("measure_clock pwm"),
        "emmc": Measure("measure_clock emmc"),
        "emmc2": Measure("measure_clock emmc2"),
        "m2mc": Measure("measure_clock m2mc"),
        "pixel": Measure("measure_clock pixel"),
        "pixel_bvb": Measure("measure_clock pixel_bvb"),
        "vec": Measure("measure_clock vec"),
        "hdmi": Measure("measure_clock hdmi"),
        "dpi": Measure("measure_clock dpi"),
    }

    volts = {
        "core": Measure("measure_volts core"),
        "sdram_c": Measure("measure_volts sdram_c"),
        "sdram_i": Measure("measure_volts sdram_i"),
        "sdram_p": Measure("measure_volts sdram_p"),
    }
    
    mr = {
        "readmr_4": Measure("readmr 4"),
        "readmr_5": Measure("readmr 5"),
        "readmr_6": Measure("readmr 6"),
        "readmr_8": Measure("readmr 8"),
    }

    readosc = {
        "readosc_1": Measure("read_ring_osc 1"),
        "readosc_2": Measure("read_ring_osc 2"),
        "readosc_3": Measure("read_ring_osc 3"),
        "readosc_4": Measure("read_ring_osc 4"),
        "readosc_5": Measure("read_ring_osc 5"),
        "readosc_6": Measure("read_ring_osc 6"),
        "readosc_7": Measure("read_ring_osc 7"),
        "readosc_8": Measure("read_ring_osc 8"),
        "readosc_9": Measure("read_ring_osc 9"),
        "readosc_10": Measure("read_ring_osc 10"),
        "readosc_11": Measure("read_ring_osc 11"),
        "readosc_12": Measure("read_ring_osc 12"),
        "readosc_13": Measure("read_ring_osc 13"),
        "readosc_14": Measure("read_ring_osc 14"),
        "readosc_15": Measure("read_ring_osc 15"),
        "readosc_16": Measure("read_ring_osc 16"),
        "readosc_17": Measure("read_ring_osc 17"),
        "readosc_18": Measure("read_ring_osc 18"),
        "readosc_19": Measure("read_ring_osc 19"),
        "readosc_20": Measure("read_ring_osc 20"),
        "readosc_21": Measure("read_ring_osc 21"),
        "readosc_22": Measure("read_ring_osc 22"),
        "readosc_23": Measure("read_ring_osc 23"),
        "readosc_24": Measure("read_ring_osc 24"),
        "readosc_25": Measure("read_ring_osc 25"),
        "readosc_26": Measure("read_ring_osc 26"),
        "readosc_27": Measure("read_ring_osc 27"),
        "readosc_28": Measure("read_ring_osc 28"),
        "readosc_29": Measure("read_ring_osc 29"),
        "readosc_30": Measure("read_ring_osc 30"),
        "readosc_31": Measure("read_ring_osc 31"),
        "readosc_32": Measure("read_ring_osc 32"),
        "readosc_33": Measure("read_ring_osc 33"),
    }

    while True:

        ### GET ALL DATA BEFORE PRINTING ###

        # Get status information
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S.%f")
        fw_version = get_vcgencmd_output(mb, "version")

        # Get processor usage information

#        cpu_percent = psutil.cpu_percent(interval=1)

        # Get Vcgencmd metrics
        for _, command in clocks.items():
            command.value = get_vcgencmd_output(mb, command.command).split('=')[1]

        arm_temp = get_vcgencmd_output(mb, "measure_temp").split('=')[1]

        for _, command in volts.items():
            command.value = get_vcgencmd_output(mb, command.command).split('=')[1]
            
        for _, command in mr.items():
            command.value = get_vcgencmd_output(mb, command.command).split(':')[5]

        for _, command in readosc.items():
            command.value = get_vcgencmd_output(mb, command.command).split('=')[1]

        # Check for throttling
        throttle_hex_value = get_vcgencmd_output(mb, "get_throttled").split('=')[1]
        throttling_status = decode_throttling(throttle_hex_value)

        # Measure PMIC telemetry
        adc_values = pmic_read_adc(mb)

        ### CLEAR THE TERMINAL BEFORE PRINTING ###
        os.system("clear")  # Use "cls" for Windows

        ### PRINT ALL THE DATA ###
        print("## System Info ##")
        print(f"timestamp: {timestamp}")
        print(f"FW Version: {fw_version}")
        print("")

        #print("## Usage ##")
        #cpu_usage = get_cpu_usage()
        #for core, usage in enumerate(cpu_usage):
        #    print(f"Core {core}: {usage:.2f}%")
        #print("")

        print("## Frequencies ##")
        for name, command in clocks.items():
            print(f"{name}: \t\t{command.value[:-6]} MHz")
        print("")

        print("## Temperature ##")
        print(f"arm: \t\t{arm_temp[:-2]}")
        print("")

        print("## Voltages ##")
        for name, command in volts.items():
            if len(name) < 7:
                print(f"{name}: \t\t{command.value}")
            else:
                print(f"{name}: \t{command.value}")
        print("")
        
        print("## Read MR ##")
        for name, command in mr.items():
            print(f"{name}: \t{command.value[1:]}")
        # decode readmr 4
        for name, command in mr.items():
            if command.command == "readmr 4":
                output = get_vcgencmd_output(mb, command.command).split(':')[5]
                value = int(output[1:])
                decoded_message = decode_readmr_4(value)
                print(f"readmr_4_msg: \t\"{decoded_message}\"")
        print("")
        
        print("## Throttle Info ##")
        print(f"Throttle Hex: {throttle_hex_value}")
        for message, status in throttling_status:
            print(f"{message}: {status}")
        print("")

        print("## PMIC Telemetry ##")
        for label, value in adc_values:
            value = value.split('=')[-1][:-1]
            print(f"{label}: {value}")
        print("")

        print("## Ring Oscillator MHz ##")
        for name, command in readosc.items():
            print(f"{name}: \t\t{command.value[:-23]} MHz")
        print("")

        with open(filename_with_timestamp, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Create a dictionary for the row data
            row_data = {
                "timestamp": timestamp,
#                "cpu_percent": cpu_percent,
                "arm_temp": arm_temp[:-2],
                "throttle_hex": throttle_hex_value,
                "UV": "No",
                "ArmFreqCap": "No",
                "CurThrottle": "No",
                "SoftTempLimit": "No",
                "UV_occured": "No",
                "ArmFreqCap_occured": "No",
                "Throttle_occured": "No",
                "SoftTempLimit_occured": "No",
            }

            # Add row_data with measure_clocks data
            for clock_name, command in clocks.items():
                row_data[clock_name + "_mhz"] = command.value[:-6]

            # Add row_data with measure_volts data
            for volt_name, command in volts.items():
                row_data[volt_name + "_volt"] = command.value[:-1]

            # Add row_data with readmr data                
            for mr_name, command in mr.items():
                row_data[mr_name] = command.value
            
            # Add row_data with pmic_read_adc() data
            for label, value in adc_values:
                row_data[label] = value.split('=')[-1][:-1]

            # Update row_data with decode_throttling() results
            for message, status in throttling_status:
                row_data[message] = status

            # Add row_data with read_ring_osc data
            for osc_name, command in readosc.items():
                row_data[osc_name] = command.value[:-23]
            
            writer.writerow(row_data)

#            time.sleep(1)  # Wait for 1 second
            
    #os.close(mb)

if __name__ == "__main__":
    main()
