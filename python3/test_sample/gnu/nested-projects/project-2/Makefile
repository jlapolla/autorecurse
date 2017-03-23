# From GNU Make manual section 4.3.
#
# https://www.gnu.org/software/make/manual/html_node/Prerequisite-Types.html

OBJDIR := objdir
OBJS := $(addprefix $(OBJDIR)/,foo.o bar.o baz.o)

$(OBJDIR)/%.o : %.c
	touch $@

.PHONY: all
all: $(OBJS)

$(OBJS): | $(OBJDIR)

$(OBJDIR):
	mkdir $(OBJDIR)

vpath %.c src

