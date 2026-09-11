# PVSnesLib 4.6.x project
PVSNESLIB_HOME ?= /home/forg3/tools/pvsneslib
export PVSNESLIB_HOME
export PATH := $(PVSNESLIB_HOME)/devkitsnes/bin:$(PVSNESLIB_HOME)/devkitsnes/tools:$(PATH)

export ROMNAME := super_home
export ROMTITLE := SUPER HOME SYSTEM
export ROMSIZE := 08
export SRAMSIZE := 0
export COUNTRY := 0

# Soundbank configuration
AUDIOFILES := res/soundbank.it
export SOUNDBANK := soundbank
SMCONVFLAGS := -s -o $(SOUNDBANK) -V -b 5

include $(PVSNESLIB_HOME)/devkitsnes/snes_rules

.PHONY: all cleanLogs bitmaps musics

$(CFILES:.c=.ps): $(SOUNDBANK).asm

assets/font.pic: assets/font.bmp
	$(GFXCONV) -u 16 -s 8 -o 2 -e 1 -R -m -t bmp -i $<

assets/icons.pic: assets/icons.bmp
	$(GFXCONV) -s 16 -o 16 -u 16 -p -t bmp -i $<

bitmaps: assets/font.pic assets/icons.pic

all: cleanLogs buildWithSummary

buildActual: bitmaps $(SOUNDBANK).asm $(ROMNAME).sfc

clean: cleanBuildRes cleanRom cleanGfx cleanAudio cleanLogs
	-rm -f assets/*.pic assets/*.pal assets/*.map assets/*.as assets/*.inc soundbank.*
