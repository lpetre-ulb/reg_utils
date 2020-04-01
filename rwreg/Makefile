SUBPACKAGES := \
        x86_64 \
        arm

SUBPACKAGES.DEBUG    := $(patsubst %,%.debug,    ${SUBPACKAGES})
SUBPACKAGES.DOC      := $(patsubst %,%.doc,      ${SUBPACKAGES})
SUBPACKAGES.RPM      := $(patsubst %,%.rpm,      ${SUBPACKAGES})
SUBPACKAGES.CLEANRPM := $(patsubst %,%.cleanrpm, ${SUBPACKAGES})
SUBPACKAGES.CLEANDOC := $(patsubst %,%.cleandoc,    ${SUBPACKAGES})
SUBPACKAGES.CLEAN    := $(patsubst %,%.clean,    ${SUBPACKAGES})

.PHONY: $(SUBPACKAGES)

build: $(SUBPACKAGES)

all: $(SUBPACKAGES) $(SUBPACKAGES.RPM) $(SUBPACKAGES.DOC)

rpm: $(SUBPACKAGES) $(SUBPACKAGES.RPM)

doc: $(SUBPACKAGES.DOC)

cleanrpm: $(SUBPACKAGES.CLEANRPM)

clean: $(SUBPACKAGES.CLEAN)

cleandoc: $(SUBPACKAGES.CLEANDOC)

$(SUBPACKAGES):
	$(MAKE) -C $@

$(SUBPACKAGES.RPM):
	$(MAKE) -C $(patsubst %.rpm,%, $@) rpm

$(SUBPACKAGES.DOC):
	$(MAKE) -C $(patsubst %.doc,%, $@) doc

$(SUBPACKAGES.CLEANRPM):
	$(MAKE) -C $(patsubst %.cleanrpm,%, $@) cleanrpm

$(SUBPACKAGES.CLEANDOC):
	$(MAKE) -C $(patsubst %.cleandoc,%, $@) cleandoc

$(SUBPACKAGES.CLEAN):
	$(MAKE) -C $(patsubst %.clean,%, $@) clean
