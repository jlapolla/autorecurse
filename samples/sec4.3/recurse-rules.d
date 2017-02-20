project/objdir/foo.o: project/foo.c | project/objdir
	@$(MAKE) --no-print-directory -C project/ objdir/foo.o
project/objdir/bar.o: project/bar.c | project/objdir
	@$(MAKE) --no-print-directory -C project/ objdir/bar.o
project/objdir/baz.o: project/baz.c | project/objdir
	@$(MAKE) --no-print-directory -C project/ objdir/baz.o
project/all: project/objdir/foo.o project/objdir/bar.o project/objdir/baz.o
	@$(MAKE) --no-print-directory -C project/ all
project/objdir:
	@$(MAKE) --no-print-directory -C project/ objdir

