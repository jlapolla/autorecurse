bar1.o: project-1/objdir/bar.o
	touch $@

bar2.o: project-2/objdir/bar.o
	touch $@

combined-foo: project-1/objdir/foo.o project-2/objdir/foo.o
	touch $@

.DEFAULT_GOAL := project-1/program

