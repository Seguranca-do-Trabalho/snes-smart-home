# PVSnesLib 4.6.x project
export ROMNAME := super_home
export ROMTITLE := SUPER HOME SYSTEM
export ROMSIZE := 08
export SRAMSIZE := 0
export COUNTRY := 0

include $(PVSNESLIB_HOME)/devkitsnes/snes_rules

.PHONY: all cleanLogs bitmaps

assets/font.pic: assets/font.bmp
	$(GFXCONV) -u 16 -s 8 -o 2 -e 1 -R -m -t bmp -i $<

assets/icons.pic: assets/icons.bmp
	$(GFXCONV) -s 16 -o 16 -u 16 -t bmp -i $<

bitmaps: assets/font.pic assets/icons.pic

all: cleanLogs buildWithSummary

buildActual: bitmaps $(ROMNAME).sfc

clean: cleanBuildRes cleanRom cleanGfx cleanLogs
	-rm -f assets/*.pic assets/*.pal assets/*.map assets/*.as assets/*.inc
