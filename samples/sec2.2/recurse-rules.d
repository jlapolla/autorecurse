project/edit : project/main.o project/kbd.o project/command.o project/display.o \
       project/insert.o project/search.o project/files.o project/utils.o
	@$(MAKE) --no-print-directory -C project/ edit

project/main.o : project/main.c project/defs.h
	@$(MAKE) --no-print-directory -C project/ main.o
project/kbd.o : project/kbd.c project/defs.h project/command.h
	@$(MAKE) --no-print-directory -C project/ kbd.o
project/command.o : project/command.c project/defs.h project/command.h
	@$(MAKE) --no-print-directory -C project/ command.o
project/display.o : project/display.c project/defs.h project/buffer.h
	@$(MAKE) --no-print-directory -C project/ display.o
project/insert.o : project/insert.c project/defs.h project/buffer.h
	@$(MAKE) --no-print-directory -C project/ insert.o
project/search.o : project/search.c project/defs.h project/buffer.h
	@$(MAKE) --no-print-directory -C project/ search.o
project/files.o : project/files.c project/defs.h project/buffer.h project/command.h
	@$(MAKE) --no-print-directory -C project/ files.o
project/utils.o : project/utils.c project/defs.h
	@$(MAKE) --no-print-directory -C project/ utils.o
project/clean :
	@$(MAKE) --no-print-directory -C project/ clean

