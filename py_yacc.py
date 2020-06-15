#! /usr/bin/env python
#coding=utf-8
import ply.yacc as yacc
from py_lex import *
from node import node,num_node

# YACC for parsing Python

def simple_node(t,name):
    t[0]=node(name)
    for i in range(1,len(t)):
        if t.slice[i].type == 'slice':
            t[0].add(t[i])
        elif t.slice[i].type == 'NUMBER':
            t[0].add(num_node(t[i]))
        else:
            t[0].add(node(t[i]))
    return t[0]

def p_program(t):
    '''program : statements'''
    if len(t)==2:
        t[0]=node('[PROGRAM]')
        t[0].add(t[1])
        
def p_statements(t):
    '''statements : statements statement
                  | statement'''
    if len(t)==3:
        t[0]=node('[STATEMENTS]')
        t[0].add(t[1])
        t[0].add(t[2])
    elif len(t)==2:
        t[0]=node('[STATEMENTS]')
        t[0].add(t[1])

def p_statement(t):
    ''' statement : assignment
                  | operation
                  | print
                  | if
                  | while
                  | for
                  | BREAK '''
    if len(t)==2:
        t[0]=node(['STATEMENT'])
        if t.slice[1].type == 'BREAK':
            t[0].add(node('[BREAK]'))
        else:
            t[0].add(t[1])
        
def p_assignment(t):
    '''assignment : VARIABLE '=' NUMBER
                 | VARIABLE '=' VARIABLE
                 | VARIABLE '=' operation
                 | slice '=' slice
                 | slice '=' VARIABLE
                 | VARIABLE '=' slice '''
    if t.slice[1].type == 'slice' or t.slice[3].type == 'slice':
        t[0] = node('[ASSIGNMENT]')
        if t.slice[1].type == 'slice':
            if t.slice[3].type == 'slice':
                t[0].add(t[1])
                t[0].add(node(t[2]))
                t[0].add(t[3])
            else:
                t[0].add(t[1])
                t[0].add(node(t[2]))
                t[0].add(node(t[3]))
        else:
            t[0].add(node(t[1]))
            t[0].add(node(t[2]))
            t[0].add(t[3])
    elif t.slice[3].type == 'operation':
        t[0]=node('[ASSIGNMENT]')
        t[0].add(node(t[1]))
        t[0].add(node(t[2]))
        t[0].add(t[3])
    elif t.slice[3].type == 'NUMBER':
        t[0]=node('[ASSIGNMENT]')
        t[0].add(node(t[1]))
        t[0].add(node(t[2]))
        t[0].add(num_node(t[3]))
    elif t.slice[3].type == 'VARIABLE':
        t[0]=node('[ASSIGNMENT]')
        t[0].add(node(t[1]))
        t[0].add(node(t[2]))
        t[0].add(node(t[3]))

def p_slice(t):
    '''slice : VARIABLE '[' VARIABLE ']' '''
    t[0] = simple_node(t, '[SLICE]')

def p_commaexpression(t):
    '''commaexpression : commaexpression ',' NUMBER
                       | NUMBER ',' NUMBER
                       | NUMBER'''
    if len(t) == 2:
        t[0] = node('[COMMAEXPRESSION]')
        t[0].add(num_node(t[1]))
    elif len(t) == 4:
        t[0] = node('[COMMAEXPRESSION]')
        if t.slice[1].type == 'NUMBER':
            t[0].add(num_node(t[1]))
            t[0].add(num_node(t[3]))
        else:
            t[0].add(t[1])
            t[0].add(num_node(t[3]))

def p_operation(t):
    '''operation : VARIABLE '+' VARIABLE
                 | VARIABLE '-' VARIABLE
                 | VARIABLE '-' NUMBER
                 | VARIABLE '+' NUMBER
                 | '[' commaexpression ']'
                 | LEN '(' VARIABLE ')'
                 | '(' VARIABLE '+' VARIABLE ')' GDIV NUMBER '''
    if len(t)==4 and t.slice[2].type!='commaexpression':
        t[0]=simple_node(t,'[OPERATION]')
    elif len(t)==4 and t.slice[2].type=='commaexpression':
        t[0] = node('[OPERATION]')
        t[0].add(node(t[1]))
        t[0].add(t[2])
        t[0].add(node(t[3]))
    elif len(t) == 5:
        t[0]=simple_node(t,'[OPERATION]')
    elif len(t) == 8:
        t[0]=simple_node(t,'[OPERATION]')

def p_print(t):
    '''print : PRINT '(' VARIABLE ')' '''
    if len(t)==5:
        t[0]=simple_node(t,'[PRINT]')

def p_if(t):
    r'''if : IF '(' condition ')' '{' statements '}'
           | IF '(' condition ')' '{' statements '}' ELIF '(' condition ')' '{' statements '}' ELSE '{' statements '}' '''
    if len(t)==8:
        t[0]=node('[IF]')
        t[0].add(t[3])
        t[0].add(t[6])
    else:
        t[0] = node('[IF]')
        t[0].add(t[3]) # condition
        t[0].add(t[6])  # statements
        t[0].add(t[10]) # condition
        t[0].add(t[13]) # statements
        t[0].add(t[17]) # break


def p_condition(t):
    '''condition : VARIABLE '>' VARIABLE
                 | VARIABLE '<' VARIABLE
                 | VARIABLE LET VARIABLE
                 | slice '>' VARIABLE
                 | slice '<' VARIABLE '''
    if len(t)==4:
        t[0]=simple_node(t,'[CONDITION]')

def p_while(t):
    r'''while : WHILE '(' condition ')' '{' statements '}' '''
    if len(t)==8:
        t[0]=node('[WHILE]')
        t[0].add(t[3])
        t[0].add(t[6])
    
def p_for(t):
    r'''for : FOR '(' assignment ';' condition ';' VARIABLE INC ')' '{' statements '}' '''
    t[0] = node('[FOR]')
    t[0].add(t[3])
    t[0].add(t[5])
    t[0].add(node(t[7]))
    t[0].add(t[11])

def p_error(t):
    print(f"Syntax error at lineno: {t.lineno}, lexpos: {t.lexpos}, type:  {t.type}, value: {t.value}")

yacc.yacc()
