# skatterbencher-77-tools
Tools and scripts used for SkatterBencher #77 - Raspberry Pi 5

- fw_vlimit: python script to override the firmware voltage limit of 1V
- oc_settings: text files with the oc parameters for each OC strategy
- slowcpu-service: files for strategy #3 to slow down the CPU before entering OS

Firmware Voltage Limit:
- firmware limits DVF voltage to 1V
- script locates firmware function that defines the limit & overrides to 1.2V
- then flush videocore cache to apply the new voltage limit
- voltage still limited by PMIC to 1.1V

noppi:
- measures number of NOPs per 100ms and translates in to effective clock frequency (ref: ElmorLabs NopBench https://skatterbencher.com/nopbench/)
- noppi_mhz.c: source code; compile with "gcc -o noppi_mhz noppi_mhz.c -pthread"
- noppi_mhz: compiled binary

OC Settings:
- oc_all: list of all overclocking parameters mentioned in SkatterBencher #77
- strategy #1: arm_freq=2900, over_voltage_delta=250000
- strategy #2: arm_freq=2900, gpu_freq=1100, v3d_freq=960, over_voltage_delta=250000
- strategy #3: arm_freq=3000, gpu_freq=1100, v3d_freq=1200, over_voltage_delta=250000
- evc2: over_voltage=8

rpi5-monlog:
- telemetry script to capture and log relevant vcgencmd telemetry.
- further development: https://github.com/SkatterBencher/rpi5-telemetry-python
- rpi5_telemetry_monlog.py: base script which updates every second
- rpi5_telemetry_monlog_fast.py: removed cpu usage telemetry and sleep; much faster updating

Slow CPU:
- slowcpu in /bin/
- slowcpu.service in /lib/systemd/system/
- enable service with "sudo systemctl enable slowcpu.service"
