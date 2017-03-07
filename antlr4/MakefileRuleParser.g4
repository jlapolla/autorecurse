parser grammar MakefileRuleParser;
options { tokenVocab=MakefileRuleLexer; superClass=app.antlr.custom.CustomParser; }

declaration : makefileRule | EOL ;
makefileRule : target+ COLON prerequisite* (PIPE orderOnlyPrerequisite*)? recipe ;
target : IDENTIFIER ;
prerequisite : IDENTIFIER ;
orderOnlyPrerequisite : IDENTIFIER ;
recipe : (RECIPE_LINE | EOL)+ | EOF ;

