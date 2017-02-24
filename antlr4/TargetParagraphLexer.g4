lexer grammar TargetParagraphLexer;

NOT_A_TARGET_PARAGRAPH : NOT_A_TARGET_LINE LINE* -> skip ;
PHONY_PARAGRAPH : PHONY_LINE LINE* -> skip ;
TARGET_PARAGRAPH : LINE+ ;
BLANK_PARAGRAPH : EOL+ -> skip ;
fragment NOT_A_TARGET_LINE : '# Not a target:' (EOL | EOF) ;
fragment PHONY_LINE : '.PHONY: ' ~'\n'* (EOL | EOF) ;
fragment LINE : ~'\n'+ (EOL | EOF) ;
fragment EOL : '\n' ;

