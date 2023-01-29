# The MIT License (MIT)
# Copyright (c) 2023 Mike Teachman
# https://opensource.org/licenses/MIT

# Purpose:  compute I2S PLL configurations for the STM32F4 and STM32F7 processors that result
#           in optimal sampling frequencies coming from the I2S Clock Generator
# Usage:    
#           1. configure parameters HSE_FREQUENCY and MICROPY_HW_CLK_PLLM
#           2. run program:  python3 stm32_calc_i2s_pll.py

# STM32 references:
# RM0090 Reference manual STM32F405/415, STM32F407/417, STM32F427/437 and STM32F429/439
# - section 6.3.23 RCC PLLI2S configuration register (RCC_PLLI2SCFGR)
# - section 28.4.4 Clock generator
# RM0385 Reference manual STM32F75xxx and STM32F74xxx
# - section 5.3.23 RCC PLLI2S configuration register (RCC_PLLI2SCFGR)
# - section 32.7.5 Clock generator

# FI2SxCLK is the output of the I2S PLL
# FI2SxCLK = HSE_FREQUENCY / MICROPY_HW_CLK_PLLM * PLLI2SN / PLLI2SR
# PLLI2SN  Min: 50, Max: 432, 
# PLLI2SR  Min: 2, Max: 7  set PLLI2SR so the I2S PLL output does not exceed 192 MHz

# Fs is the I2S sampling frequency that is observed at the I2S SCK output
# Fs = FI2SxCLK / (32 x (CHLEN + 1 ) x ((2 x I2SDIV) + ODD))
# CHLEN = 0 for 16 bits, 1 for 32 bits
# I2SDIV range, 0-255
# ODD either 0 or 1

HSE_FREQUENCY = 12_000_000
MICROPY_HW_CLK_PLLM = 12

print("HSE_FREQUENCY:", HSE_FREQUENCY)
print("MICROPY_HW_CLK_PLLM:", MICROPY_HW_CLK_PLLM, "\n")

for chlen in (0, 1):
    for freq in (8_000, 11_025, 12_000, 16_000, 22_050, 24_000, 32_000, 44_100, 48_000):
        for pllisn in range(50, 433):
            for plli2sr in range(2, 8):
                FI2SxCLK = HSE_FREQUENCY / MICROPY_HW_CLK_PLLM * pllisn / plli2sr
                if FI2SxCLK < 192_000_000:
                    for i2sdiv in range(1, 255):
                        for odd in (0,1):
                            Fs = FI2SxCLK / (32 * (chlen + 1 ) * ((2 * i2sdiv) + odd))
                            error = (abs(Fs - freq) / freq) * 100
                            if error < 0.002: 
                                str = f"{16 if chlen==0 else 32}, " \
                                      f"{freq}, " \
                                      f"{pllisn}, " \
                                      f"{plli2sr}, " \
                                      f"/* i2sdiv: {i2sdiv}, " \
                                      f"odd: {odd}, " \
                                      f"error%: {error:.4f} */"
                                print(str)
