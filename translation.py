#! /usr/bin/env python
#coding=utf-8
from __future__ import division


v_table={} # variable table


def update_v_table(name,value):
    v_table[name]=value


def is_slice(name):
    return '[SLICE]' == name


def trans(node):
    # Assignment
    if node.getdata()=='[ASSIGNMENT]': 
        '''assignment : VARIABLE '=' NUMBER
                      | VARIABLE '=' VARIABLE
                      | VARIABLE '=' operation
                      | VARIABLE '=' slice 
                      | slice '=' slice
                      | slice '=' VARIABLE '''
        if not is_slice(node.getchild(0).getdata()):
            if node.getchild(2).getdata() == '[OPERATION]' or \
                    is_slice(node.getchild(2).getdata()):
                trans(node.getchild(2))
                value = node.getchild(2).getvalue()
            elif node.getchild(2).getdata() in v_table:
                value = v_table[node.getchild(2).getdata()]
            else:
                value = node.getchild(2).getvalue()
            node.getchild(0).setvalue(value)
            update_v_table(node.getchild(0).getdata(),value)
        else:
            # slice
            trans(node.getchild(0))
            if is_slice(node.getchild(2).getdata()):
                trans(node.getchild(2))
                slice_ = node.getchild(0)
                i = slice_.slice_index
                v_table[slice_.slice_variable][i] = node.getchild(2).getvalue()
                node.getchild(0).setvalue(v_table[slice_.slice_variable][i])
            else: # variable
                slice_ = node.getchild(0)
                i = slice_.slice_index
                v_table[slice_.slice_variable][i] = v_table[node.getchild(2).getdata()]
                node.getchild(0).setvalue(v_table[slice_.slice_variable][i])
    # Operation
    elif node.getdata()=='[OPERATION]':
        '''operation : VARIABLE '+' VARIABLE
                    | VARIABLE '-' VARIABLE
                    | VARIABLE '-' NUMBER
                    | VARIABLE '+' NUMBER
                    | '[' commaexpression ']'
                    | LEN '(' VARIABLE ')' 
                    | '(' VARIABLE '+' VARIABLE ')' GDIV NUMBER '''
        if len(node._children) == 4:
            node.setvalue(len(v_table[node.getchild(2).getdata()]))
        elif node.getchild(1).getdata() == '+':
            arg0=v_table[node.getchild(0).getdata()]
            if node.getchild(2).getdata() in v_table:
                arg1=v_table[node.getchild(2).getdata()]
            else:
                arg1 = node.getchild(2).getvalue()
            node.setvalue(arg0 + arg1)
        elif node.getchild(1).getdata() == '-':
            arg0=v_table[node.getchild(0).getdata()]
            if node.getchild(2).getdata() in v_table:
                arg1=v_table[node.getchild(2).getdata()]
            else:
                arg1 = node.getchild(2).getvalue()
            node.setvalue(arg0 - arg1)
        elif len(node._children) == 7:
            var1 = v_table[node.getchild(1).getdata()]
            var2 = v_table[node.getchild(3).getdata()]
            num = node.getchild(6).getvalue()
            node.setvalue((var1 + var2)//num)
        else:
            # commaexpression
            trans(node.getchild(1))
            node.setvalue(eval('[{}]'.format(node.getchild(1).getvalue())))

    # Print
    elif node.getdata()=='[PRINT]':
        '''print : PRINT '(' VARIABLE ')' '''
        arg0=v_table[node.getchild(2).getdata()]
        print(arg0)
    
    # If
    elif node.getdata()=='[IF]':
        r'''IF [CONDITION] [STATEMENTS] 
            IF [CONDITION] [STATEMENTS] [CONDITION] [STATEMENTS] [STATEMENTS]'''
        children=node.getchildren()
        if len(children) == 5:
            if trans(children[0]):
                v = trans(children[1])
                if v == '[BREAK]':
                    node.setvalue('[BREAK]')
            elif trans(children[2]):
                v = trans(children[3])
                if v == '[BREAK]':
                    node.setvalue('[BREAK]')
            else:
                v = trans(children[4])
                if v == '[BREAK]':
                    node.setvalue('[BREAK]')

        elif len(children) == 2:
            trans(children[0])
            condition=children[0].getvalue()
            if condition:
                for c in children[1:]:
                    trans(c)

    elif node.getdata()=='[FOR]':
        r'''FOR : assignment condition VARIABLE statements'''
        children=node.getchildren()
        trans(children[0])
        while trans(children[1]):
            for c in children[3:]:
                trans(c)
            update_v_table(children[2].getdata(), v_table[children[2].getdata()] + 1)

    # While
    elif node.getdata()=='[WHILE]':
        r'''while : WHILE '(' condition ')' '{' statements '}' '''
        children=node.getchildren()
        while trans(children[0]):
            v = trans(children[1])
            if v == '[BREAK]':
                break

    # Condition
    elif node.getdata()=='[CONDITION]':
        '''condition : VARIABLE '>' VARIABLE
                     | VARIABLE '<' VARIABLE
                     | VARIABLE LET VARIABLE
                     | slice '>' VARIABLE 
                     | slice '<' VARIABLE '''
        if is_slice(node.getchild(0).getdata()):
            trans(node.getchild(0))
            v = node.getchild(0).slice_variable
            i = node.getchild(0).slice_index
            op=node.getchild(1).getdata()
            arg0 = v_table[v][i]
            arg1 = v_table[node.getchild(2).getdata()]
            if op == '>':
                node.setvalue(arg0 > arg1)
            elif op == '<':
                node.setvalue(arg0 < arg1)
        else:
            arg0=v_table[node.getchild(0).getdata()]
            arg1=v_table[node.getchild(2).getdata()]
            op=node.getchild(1).getdata()
            if op=='>':
                node.setvalue(arg0>arg1)
            elif op=='<':
                node.setvalue(arg0<arg1)
            elif op == '<=':
                node.setvalue(arg0 <= arg1)

    elif node.getdata() == '[SLICE]':
        node.slice_variable = node.getchild(0).getdata()
        v = v_table[node.getchild(0).getdata()]
        node.slice_index = int(v_table[node.getchild(2).getdata()])
        i = node.slice_index
        node.setvalue(v[i])
    
    elif node.getdata() == '[COMMAEXPRESSION]':
        '''commaexpression : commaexpression ',' NUMBER
                           | NUMBER ',' NUMBER
                           | NUMBER'''
        if len(node._children) == 1:
            node.setvalue(node.getchild(0).getvalue())
        else:
            if node.getchild(0).getdata() == '[COMMAEXPRESSION]':
                trans(node.getchild(0))
            node.setvalue("{},{}".format(node.getchild(0).getvalue(), node.getchild(1).getvalue()))

    elif node.getdata() == '[BREAK]':
        node.setvalue('[BREAK]')

    else:

        for c in node.getchildren():
            v = trans(c)
            if v == '[BREAK]':
                node.setvalue('[BREAK]')
    
    return node.getvalue()
