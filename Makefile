antlr4/MakefileRuleLexer.py antlr4/MakefileRuleLexer.tokens: antlr4/MakefileRuleLexer.g4
	antlr4 -Dlanguage=Python3 $<

antlr4/MakefileRuleParser.py antlr4/MakefileRuleParser.tokens: antlr4/MakefileRuleParser.g4 antlr4/MakefileRuleLexer.tokens
	antlr4 -Dlanguage=Python3 -lib antlr4 $<

antlr4/TargetParagraphLexer.py antlr4/TargetParagraphLexer.tokens: antlr4/TargetParagraphLexer.g4
	antlr4 -Dlanguage=Python3 $<

ANTLR += python3/autorecurse/gnumake/grammar/MakefileRuleLexer.py
python3/autorecurse/gnumake/grammar/MakefileRuleLexer.py: antlr4/MakefileRuleLexer.py
	printf '%s\n' 'import autorecurse.lib.antlr4.custom' | cat - $< 1>$@

ANTLR += python3/autorecurse/gnumake/grammar/MakefileRuleParser.py
python3/autorecurse/gnumake/grammar/MakefileRuleParser.py: antlr4/MakefileRuleParser.py
	printf '%s\n' 'import autorecurse.lib.antlr4.custom' | cat - $< | sed '7d;8d' 1>$@

ANTLR += python3/autorecurse/gnumake/grammar/TargetParagraphLexer.py
python3/autorecurse/gnumake/grammar/TargetParagraphLexer.py: antlr4/TargetParagraphLexer.py
	printf '%s\n' 'import autorecurse.lib.antlr4.custom' | cat - $< 1>$@

.PHONY: antlr
antlr: $(ANTLR)

.PHONY: test
test: $(ANTLR)
	cd python3 && python3 -m unittest discover

profile.prof: $(ANTLR)
	python3 -m cProfile -o $@ python3/test_main.py

cachegrind.out.0: profile.prof
	pyprof2calltree -o $@ -i $<

.PHONY: profile
profile: clean-profile cachegrind.out.0
	kcachegrind cachegrind.out.0

.PHONY: clean-profile
clean-profile:
	rm -f profile.prof cachegrind.out.0

.DEFAULT_GOAL := antlr

