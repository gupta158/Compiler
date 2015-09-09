grammar LittleExpr;

/* Program */
program: PROGRAM identifier BEGIN pgm_body END ;
identifier: IDENTIFIER;
pgm_body: decl func_declarations;
decl: string_decl decl | var_decl decl | ;

/* Global String Declaration */
string_decl: STRING identifier COLEQ stringliteral ;
stringliteral: STRINGLITERAL;

/* Variable Declaration */
var_decl: var_type id_list ;
var_type: FLOAT | INT ;
any_type: var_type | VOID ;
id_list: identifier id_tail ;
id_tail: COMMA identifier id_tail | ;

/* Function Paramater List */
param_decl_list: param_decl param_decl_tail | ;
param_decl: var_type identifier ;
param_decl_tail: COMMA param_decl param_decl_tail | ;


/* Function Declarations */
func_declarations: func_decl func_declarations | ;
func_decl: FUNCTION any_type identifier (param_decl_list) BEGIN func_body END;
func_body: decl stmt_list;


/* Statement List */
stmt_list: stmt stmt_list | ;
stmt: base_stmt | if_stmt | for_stmt ;
base_stmt: assign_stmt | read_stmt | write_stmt | return_stmt ;

//Basic statment
assign_stmt: assign_expr SEMICOLON;
assign_expr: identifier COLEQ expr;
read_stmt: READ OPENPAR id_list CLOSEPAR;
write_stmt: WRITE OPENPAR id_list CLOSEPAR;
return_stmt: RETURN expr;

//EXPRESIONS
expr: expr_prefix factor;
expr_prefix: expr_prefix factor addop | ;
factor: factor_prefix postfix_expr;
factor_prefix: factor_prefix postfix_expr mulop | ;
postfix_expr: primary | call_expr;
call_expr: identifier OPENPAR expr_list CLOSEPAR;
expr_list: expr expr_list_tail | ;
expr_list_tail: COMMA expr expr_list_tail | ;
primary: OPENPAR expr CLOSEPAR | identifier | INTLITERAL | FLOATLITERAL;
addop: ADD | SUB;
mulop: MUL | DIV;

/* Complex Statements and Condition */ 
if_stmt: IF OPENPAR cond CLOSEPAR decl stmt_list else_part FI;
else_part: ELSE decl stmt_list | ;
cond: expr compop expr;
compop: LT | GT | EQU | NEQ| LEQ | GEQ;

init_stmt: assign_expr | ;
incr_stmt: assign_expr | ;

/* ECE 468 students use this version of for_stmt */
for_stmt: FOR OPENPAR init_stmt SEMICOLON cond SEMICOLON incr_stmt CLOSEPAR decl stmt_list ROF ;

// KEYWORD: PROGRAM
// 	   | BEGIN
// 	   | END
// 	   | FUNCTION
// 	   | READ
// 	   | WRITE
// 	   | IF
// 	   | ELSE
// 	   | FI
// 	   | FOR
// 	   | ROF
// 	   | CONTINUE
// 	   | BREAK
// 	   | RETURN
// 	   | INT
// 	   | VOID
// 	   | STRING
// 	   | FLOAT ;

PROGRAM: 'PROGRAM';
BEGIN: 'BEGIN';
END: 'END';
FUNCTION: 'FUNCTION';
READ: 'READ';
WRITE: 'WRITE';
IF: 'IF';
ELSE: 'ELSE';
FI: 'FI';
FOR: 'FOR';
ROF: 'ROF';
CONTINUE: 'CONTINUE';
BREAK: 'BREAK';
INT: 'INT';
VOID: 'VOID';
STRING: 'STRING';
FLOAT: 'FLOAT';
RETURN: 'RETURN';

IDENTIFIER: [a-zA-Z][a-zA-Z0-9]* ;

// OPERATOR: MUL
// 		| ADD
// 		| SUB
// 		| DIV
// 		| EQU
// 		| NEQ
// 		| LT
// 		| LEQ
// 		| GT
// 		| GEQ
// 		| OPENPAR
// 		| CLOSEPAR
// 		| SEMICOLON
// 		| COMMA
// 		| COLEQ
// 		;

STRINGLITERAL: '"'('\\"' | ~['"'])*'"';

FLOATLITERAL: [0-9]*'.'[0-9]+;
INTLITERAL: [0-9]+;

MUL: '*';
ADD: '+';
SUB: '-';
DIV: '/';
EQU: '=';
NEQ: '!=';
LT: '<';
LEQ: '<=';
GT: '>';
GEQ: '>=';
OPENPAR: '(';
CLOSEPAR: ')';
SEMICOLON: ';';
COMMA: ',';
COLEQ: ':=';


WS: [ \r\t\n]+ -> skip ;

COMMENT: '--'~[NEWLINE]* '\r'? NEWLINE -> skip;

NEWLINE: '\n';