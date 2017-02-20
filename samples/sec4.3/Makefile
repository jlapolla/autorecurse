foo2.o: project/objdir/foo.o
	touch $@

database: project/Makefile
	-$(MAKE) -qp -C project/ 1>database

clean:
	-rm database edit2

include recurse-rules.d

