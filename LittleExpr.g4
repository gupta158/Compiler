grammar LittleExpr;

keyword : KEYWORD;


KEYWORD:	(PROGRAM|'BEGIN'|'END'|'FUNCTION'|'READ'|'WRITE'|'IF'|'ELSE'|'FI'|'FOR'|'ROF'|'CONTINUE'|'BREAK'|'RETURN'|'INT'|'VOID'|'STRING'|'FLOAT') {print("Hello world")};	//('PROGRAM'|'BEGIN'|'END'|'FUNCTION'|'READ'|'WRITE'|'IF'|'ELSE'|'FI'|'FOR'|'ROF'|'CONTINUE'|'BREAK'|'RETURN'|'INT'|'VOID'|'STRING'|'FLOAT');

INDENTIFER: [a-zA-Z][a-zA-Z0-9]* {print("Goodbye, World")};

OPERATOR: MUL
		| ADD;

// STRINGLITERAL:;

// FLOATLITERAL:;
// INTLITERAL:;

PROGRAM: 'PROGRAM';

MUL: '*';

ADD: '+';

WS: [ \r\t\n]+ -> skip ;

COMMENT: '--'~[NEWLINE]* '\r'? NEWLINE -> skip;

NEWLINE: '\n';

/*
	todo:
	define operators
	define literals
	define keywords in detail
	*/