edit2: project/edit
	touch $@

database: project/Makefile
	-$(MAKE) -qp -C project/ 1>database

clean: project/clean
	rm database edit2

include recurse-rules.d

