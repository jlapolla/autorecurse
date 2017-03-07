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

ANTLR += python3/app/antlr/grammar/MakefileRuleLexer.py
python3/app/antlr/grammar/MakefileRuleLexer.py: antlr4/MakefileRuleLexer.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< 1>$@

ANTLR += python3/app/antlr/grammar/MakefileRuleParser.py
python3/app/antlr/grammar/MakefileRuleParser.py: antlr4/MakefileRuleParser.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< | sed '7d;8d' 1>$@

ANTLR += python3/app/antlr/grammar/ParagraphLexer.py
python3/app/antlr/grammar/ParagraphLexer.py: antlr4/ParagraphLexer.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< 1>$@

ANTLR += python3/app/antlr/grammar/TargetParagraphLexer.py
python3/app/antlr/grammar/TargetParagraphLexer.py: antlr4/TargetParagraphLexer.py
	printf '%s\n' 'import app.antlr.custom' | cat - $< 1>$@

.PHONY: antlr
antlr: $(ANTLR)

.PHONY: test
test: $(ANTLR)
	python3 -m unittest discover -s python3

profile.prof: $(ANTLR)
	python3 -m cProfile -o $@ python3/test_main.py

cachegrind.out.0: profile.prof
	pyprof2calltree -o $@ -i $<

.PHONY: profile
profile: cachegrind.out.0
	kcachegrind cachegrind.out.0

.PHONY: profile-clean
profile-clean:
	rm -f profile.prof cachegrind.out.0

.DEFAULT_GOAL := antlr

