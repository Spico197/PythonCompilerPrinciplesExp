#! /usr/bin/env python
#coding=utf-8

def clear_text(text):
    lines=[]
    for line in text.split('\n'):
        line=line.strip()
        if len(line)>0 and not line.startswith('#'):
            lines.append(line)
    return ' '.join(lines)
