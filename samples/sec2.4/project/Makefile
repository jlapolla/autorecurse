objects = main.o kbd.o command.o display.o \
          insert.o search.o files.o utils.o

edit : $(objects)
	touch $@
main.o : main.c defs.h
	touch $@
kbd.o : kbd.c defs.h command.h
	touch $@
command.o : command.c defs.h command.h
	touch $@
display.o : display.c defs.h buffer.h
	touch $@
insert.o : insert.c defs.h buffer.h
	touch $@
search.o : search.c defs.h buffer.h
	touch $@
files.o : files.c defs.h buffer.h command.h
	touch $@
utils.o : utils.c defs.h
	touch $@
clean :
	rm edit $(objects)

