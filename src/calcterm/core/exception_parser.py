from threading import local
from typing import Dict
import sympy,re

def parse_expr(expr:str,local_dict:Dict=None,global_dict:Dict=None,evaluate:bool=True):
    compile(expr,'Expression','eval')
    res=sympy.parse_expr(expr,local_dict=local_dict,global_dict=global_dict,evaluate=evaluate)
    return res

def syntaxErrTranslate(e:SyntaxError):
    args=e.args[1]
    print(args)
    fname=args[0]
    start=args[2]
    text=args[3]
    end=args[5]
    if start==end==0:
        return f'表达式{text.__repr__()}不完整'
    if start==end or start==end-1:
        return f'在表达式{text.__repr__()}的第{start}个字符{text[start-1].__repr__()}存在非法语法'
    return f'在表达式{text.__repr__()}的第{start}个字符至第{end-1}个字符中的内容{text[start-1:end-1].__repr__()}存在非法语法'

def valueErrTranslate(e:ValueError):
    arg=e.args[1]
    for i,j in enumerate(cpatterns):
        if re.fullmatch(j,arg):
            return translates[i]
    return f'未知错误：{e.__repr__()}'


patterns=[r'^specify dummy variables for .*$',r'^ specify dummy variables for .*\. If the function contains more than one free symbol, a dummy variable should be supplied explicitly e\.g\. FourierSeries\(m\*n\*\*2, \(n, -pi, pi\)\)$',r'^ specify dummy variables for .*\. If the formula contains more than one free symbol, a dummy variable should be supplied explicitly e\.g\., SeqFormula\(m\*n\*\*2, \(n, 0, 5\)\)$']

translates=['被积分对象需要指定积分变量。尝试使用“int(..., x)”(x为表达式中的符号)。',
            '傅里叶变换的表达式需要指定主变量。尝试使用“fourier_series(..., (x, ..., ...))”(x为表达式中的符号)',
            '']

cpatterns=[re.compile(i) for i in patterns]