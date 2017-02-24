antlr4/LineLexer.py antlr4/LineLexer.tokens: antlr4/LineLexer.g4
	antlr4 -Dlanguage=Python3 $<

antlr4/ParagraphLexer.py antlr4/ParagraphLexer.tokens: antlr4/ParagraphLexer.g4
	antlr4 -Dlanguage=Python3 $<

ANTLR += python3/app/antlr/lexline.py
python3/app/antlr/lexline.py: antlr4/LineLexer.py
	cp $< $@

ANTLR += python3/app/antlr/lexparagraph.py
python3/app/antlr/lexparagraph.py: antlr4/ParagraphLexer.py
	cp $< $@

.PHONY: antlr
antlr: $(ANTLR)

.PHONY: test
test: antlr
	python3 -m unittest discover -s python3

.DEFAULT_GOAL := antlr

