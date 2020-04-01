PETA_STAGE ?= /opt/gem-peta-stage/ctp7
ifeq "$(wildcard $(PETA_STAGE) )" ""
$(error "Error: PETA_STAGE environment does not point to an existing direcotory. ($(PETA_STAGE) does not exist))
endif

BUILD_HOME   := $(shell dirname `cd ../../; pwd`)
Project      := reg_utils
Package      := rwreg
ShortPackage := rwreg
LongPackage  := rwreg
PackageName  := $(ShortPackage)
PackagePath  := $(shell pwd)
PackageDir   := pkg/$(ShortPackage)
Arch         := arm
Packager     := Mykhailo Dalchenko

RWREG_VER_MAJOR:=$(shell $(BUILD_HOME)/$(Project)/config/tag2rel.sh | awk '{split($$0,a," "); print a[1];}' | awk '{split($$0,b,":"); print b[2];}')
RWREG_VER_MINOR:=$(shell $(BUILD_HOME)/$(Project)/config/tag2rel.sh | awk '{split($$0,a," "); print a[2];}' | awk '{split($$0,b,":"); print b[2];}')
RWREG_VER_PATCH:=$(shell $(BUILD_HOME)/$(Project)/config/tag2rel.sh | awk '{split($$0,a," "); print a[3];}' | awk '{split($$0,b,":"); print b[2];}')

include $(BUILD_HOME)/$(Project)/config/mfCommonDefs.mk
include $(BUILD_HOME)/$(Project)/config/mfZynq.mk
include $(BUILD_HOME)/$(Project)/config/mfRPMRules.mk

IncludeDirs= ${BUILD_HOME}/${Project}/${Package}/${Arch}/include
INC=$(IncludeDirs:%=-I%)

LIB_ARM_RWREG_OBJS=src/libmemsvc.o src/rwreg.o
LIB_ARM_RWREG=${BUILD_HOME}/${Project}/${Package}/${Arch}/lib/librwreg.so

.PHONY: clean rpc prerpm

default:
	@echo "Running default target"
	$(MakeDir) $(PackageDir)

_rpmprep: preprpm
	@echo "Running _rpmprep target"
preprpm: default
	@echo "Running preprpm target"
	@cp -rf lib $(PackageDir)

build: $(LIB_ARM_RWREG)

_all: $(LIB_ARM_RWREG)

$(LIB_ARM_RWREG):$(LIB_ARM_RWREG_OBJS)
	@mkdir -p ${BUILD_HOME}/${Project}/${Package}/${Arch}/lib/
	$(CXX) -std=c++0x $(LDFLAGS) $(INC) -fnon-call-exceptions -shared -o $@ $(LIB_ARM_RWREG_OBJS) 

%.o: %.c
	$(CC) -std=gnu99 -c $(CFLAGS) $(INC) -o $@ $<
%.o: %.cc
	$(CXX) -std=c++0x -c $(CFLAGS) $(INC) -o $@ $<

clean: cleanrpm
	-${RM} ${LIB_ARM_RWREG} ${LIB_ARM_RWREG_OBJS}
	-rm -rf $(PackageDir)

doc: 
	@echo "TO DO"

cleandoc: 
	@echo "TO DO"
