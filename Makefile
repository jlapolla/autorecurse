antlr4/LineLexer.py antlr4/LineLexer.tokens: antlr4/LineLexer.g4
	antlr4 -Dlanguage=Python3 $<

antlr4/MakefileRuleLexer.py antlr4/MakefileRuleLexer.tokens: antlr4/MakefileRuleLexer.g4
	antlr4 -Dlanguage=Python3 $<

antlr4/MakefileRuleParser.py antlr4/MakefileRuleParser.tokens: antlr4/MakefileRuleParser.g4 antlr4/MakefileRuleLexer.tokens
	antlr4 -Dlanguage=Python3 -lib antlr4 $<

antlr4/ParagraphLexer.py antlr4/ParagraphLexer.tokens: antlr4/ParagraphLexer.g4
	antlr4 -Dlanguage=Python3 $<

antlr4/TargetParagraphLexer.py antlr4/TargetParagraphLexer.tokens: antlr4/TargetParagraphLexer.g4
	antlr4 -Dlanguage=Python3 $<

ANTLR += python3/app/antlr/grammar/LineLexer.py
python3/app/antlr/grammar/LineLexer.py: antlr4/LineLexer.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< 1>$@

ANTLR += python3/app/antlr/lexmakefilerule.py
python3/app/antlr/lexmakefilerule.py: antlr4/MakefileRuleLexer.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< 1>$@

ANTLR += python3/app/antlr/parsemakefilerule.py
python3/app/antlr/parsemakefilerule.py: antlr4/MakefileRuleParser.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< | sed '7d;8d' 1>$@

ANTLR += python3/app/antlr/grammar/ParagraphLexer.py
python3/app/antlr/grammar/ParagraphLexer.py: antlr4/ParagraphLexer.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< 1>$@

ANTLR += python3/app/antlr/lextargetparagraph.py
python3/app/antlr/lextargetparagraph.py: antlr4/TargetParagraphLexer.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< 1>$@

.PHONY: antlr
antlr: $(ANTLR)

.PHONY: test
test: antlr
	python3 -m unittest discover -s python3

.DEFAULT_GOAL := antlr

