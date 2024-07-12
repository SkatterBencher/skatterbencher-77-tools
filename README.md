# skatterbencher-77-tools
Tools and scripts used for SkatterBencher #77 - Raspberry Pi 5

- oc_settings: text files with the oc parameters for each OC strategy
- slowcpu-service: files for strategy #3 to slow down the CPU before entering OS

OC Settings:
- oc_all: list of all overclocking parameters mentioned in SkatterBencher #77
- strategy #1: arm_freq=2900, over_voltage_delta=250000
- strategy #2: arm_freq=2900, gpu_freq=1100, v3d_freq=960, over_voltage_delta=250000
- strategy #3: arm_freq=3000, gpu_freq=1100, v3d_freq=1200, over_voltage_delta=250000
- evc2: over_voltage=8

Slow CPU:
- slowcpu in /bin/
- slowcpu.service in /lib/systemd/system/
- enable service with "sudo systemctl enable slowcpu.service"
