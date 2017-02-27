parser grammar MakefileRuleParser;
options {tokenVocab=MakefileRuleLexer;}

makefileRule : target+ COLON prerequisite* (PIPE orderOnlyPrerequisite*)? recipe ;
target : IDENTIFIER ;
prerequisite : IDENTIFIER ;
orderOnlyPrerequisite : IDENTIFIER ;
recipe : (RECIPE_TEXT | EOL)+ | EOF ;

