import sympy,keyword
from sympy.core.function import AppliedUndef
from typing import Dict,List,TypedDict
from .struct_template import *

glob={
    '__builtins__':{},
    'pi':sympy.pi,
    'E':sympy.E,
    'I':sympy.I,
    'simp':sympy.simplify,
    'logcombine':sympy.logcombine,
    'abs':sympy.Abs,
    'factor':sympy.factor,
    'diff':sympy.diff,
    'int':sympy.integrate,
    'sqrt':sympy.sqrt,
    'ln':lambda x:sympy.log(x),
    'lg':lambda x:sympy.log(x,10),
    'log':lambda x,base:sympy.log(x,base),
    'lim':sympy.limit,
    'taylor':sympy.series,
    'sin':sympy.sin,
    'cos':sympy.cos,
    'tan':sympy.tan,
    'cot':sympy.cot,
    'sec':sympy.sec,
    'csc':sympy.csc,
    'arcsin':sympy.asin,
    'arccos':sympy.acos,
    'arctan':sympy.atan,
    'arccot':sympy.acot,
    'arccsc':sympy.acsc,
    'arcsec':sympy.asec,
    'eval':sympy.N,
    'inf':sympy.oo,

    'LambertW':sympy.LambertW,

    'CRootOf':sympy.CRootOf,
    'ComplexRootOf':sympy.ComplexRootOf,
    'RootSum':sympy.RootSum,
    'rootof':sympy.rootof,

    'Integer':sympy.Integer,
    'Float':sympy.Rational,
    # 'Function':sympy.Function,
    # 'Symbol':sympy.Symbol,

    'solve':sympy.solve
}

class SymbolTracer():
    def __init__(self):
        self.symbols=set()
        self.functions=set()

    def Symbol(self,name:str,**assumptions):
        '''sympy.Symbol() function with tracing'''
        self.symbols.add(name)
        return sympy.Symbol(name,**assumptions)
    
    def Function(self,name:str,**assumptions):
        '''sympy.Function() function with tracing'''
        self.functions.add(name)
        return sympy.Function(name,**assumptions)

# def localDictGen(vars:Dict[str,str]):
#     '''
#     localDictGen:根据变量标识符+显示名称生成sympy局部变量命名空间字典
    
#     :param vars: 变量表
#     :type vars: Dict
#     '''
#     local={}
#     for id,name in vars.items():
#         if type(id)!=str or type(name)!=str:
#             raise TypeError('Keys and values must be strings.')
#         if keyword.iskeyword(id):
#             raise ValueError('Keys must not be keyword.')
#         local[id]=sympy.Symbol(name)
#     return local

def localDictGen(vars:List[Variable],funcs:List[UndefinedFunction]):# -> dict:
    local={}
    for i in vars:
        local[i['id']]=sympy.Symbol(i['name'],**i['assumptions'])
    for i in funcs:
        local[i['id']]=sympy.Function(i['name'],**i['assumptions'])
    return local

def errMsgGen(tracer:SymbolTracer):
    ERR_result=[]
    if symbols:=sorted(list(tracer.symbols)):
        ERR_result.append(f'未定义变量:{",".join(symbols)}')
    if functions:=sorted(list(tracer.functions)):
        ERR_result.append(f'未知函数:{",".join(functions)}')
    return '错误：'+'; '.join(ERR_result) if ERR_result else None

def evalf(exp:str,digit:int):
    result=sympy.parse_expr(f'simplify({exp})')
    return str(result.evalf(digit))

def simplify(exp:str):
    return sympy.parse_expr(f'simplify({exp})')

def parse(exp:str,vars:Dict[str,str]={}):
    '''
    parse:Parse and evaluate expressions written in string.
    "parse2" function is recommended for parsing sympy expressions.
    
    :param exp: Expressions written in string
    :type exp: str
    :param vars: Defined variables
    :type vars: dict
    '''
    local=localDictGen(vars)
    try:
        result=eval(exp,glob,local)
    except Exception as e:
        return e
    return str(result).replace('log','ln')

def calc(exp:str,vars:List[Variable],funcs:List[UndefinedFunction],ifeval:bool=False,digit=15) -> str:
    '''
    parse2:解析Sympy表达式
    
    :param exp: 表达式
    :type exp: str
    :param vars: 变量字典(变量标识符名:变量显示名)
    :type vars: dict
    :param funcs: 函数字典(函数标识符名:函数显示名)
    :type funcs: dict
    :param ifeval: 输出数值形式
    :type ifeval: bool
    :param digit: 有效数字位数
    :return: 表达式结果
    :rtype: str
    '''
    tracer=SymbolTracer()
    local=localDictGen(vars,funcs)
    local['Symbol']=tracer.Symbol
    local['Function']=tracer.Function

    try:
        result=sympy.parse_expr(exp,local_dict=local,global_dict=glob)
        ERR_result=errMsgGen(tracer)
        if ERR_result:
            return ERR_result
        if ifeval:
            result=sympy.N(result,digit)
    except Exception as e:
        result=repr(e)
    
    return str(result).replace('log','ln')

def lagrange(lm:List[str],tg:str,vars:List[Variable],funcs:List[UndefinedFunction]):
    lambdas=[sympy.Symbol(f'λ_{i}',real=1) for i in range(1,len(lm)+1)]
    tracer=SymbolTracer()
    local=localDictGen(vars,funcs)
    variables=list(local.values())+lambdas
    local['Symbol']=tracer.Symbol
    local['Function']=tracer.Function
    
    lm_exprs=[sympy.parse_expr(i,global_dict=glob,local_dict=local) for i in lm]
    tg_expr=sympy.parse_expr(tg,global_dict=glob,local_dict=local)

    ERR_result=errMsgGen(tracer)
    if ERR_result:
        return ERR_result

    Lag=tg_expr
    for i,lamda in enumerate(lambdas):
        Lag+=lamda*lm_exprs[i]
    print(Lag,variables)
    expr=[sympy.diff(Lag,i) for i in variables]
    print(expr)
    solves=sympy.solve(expr)
    if type(solves)==dict:solves=[solves]
    print(solves)
    for i in solves:
        res=sympy.simplify(Lag.subs(i))
        print(res)
        i['result']=res
    return solves

def solver(expr:List[str],vars:List[Variable],funcs:List[UndefinedFunction]):
    tracer=SymbolTracer()
    local=localDictGen(vars,funcs)
    local['Symbol']=tracer.Symbol5
    local['Function']=tracer.Function

    exprs=[sympy.parse_expr(i,global_dict=glob,local_dict=local) for i in expr]

    ERR_result=errMsgGen(tracer)
    if ERR_result:
        return ERR_result

    symbols=list(set(j for i in exprs for j in i.free_symbols))
    symbols.sort(key=lambda i:i.name)
    tg=yield list(map(str,symbols))
    target=[symbols[i] for i in range(len(symbols)) if tg[i]]

    result=sympy.solve(exprs,*target,dict=True)
    yield result

def smartsolver(expr:List[str],vars:List[Variable]):
    tracer=SymbolTracer()
    local=localDictGen(vars)
    local['Symbol']=tracer.Symbol
    local['Function']=tracer.Function

    exprs=[sympy.parse_expr(i,global_dict=glob,local_dict=local) for i in expr]

    ERR_result=errMsgGen(tracer)
    if ERR_result:
        return ERR_result

    symbols=list(set(j for i in exprs for j in i.free_symbols))
    symbols.sort(key=lambda i:i.name)
    tg=yield list(map(str,symbols))
    target=[symbols[i] for i in range(len(symbols)) if tg[i]]

    result=sympy.solve(exprs,*target,dict=True)
    if result==[]:
        result=[{symbol:i[index] for index,symbol in enumerate(target)}
                for i in list(sympy.nonlinsolve(exprs,*target))]
    yield result

def dsolver(expr:List[str],vars:List[Variable],functions:List[UndefinedFunction]):
    tracer=SymbolTracer()
    local=localDictGen(vars,functions)
    local['Symbol']=tracer.Symbol
    local['Function']=tracer.Function

    exprs:List[sympy.Expr]=[sympy.parse_expr(i,global_dict=glob,local_dict=local) for i in expr]

    ERR_result=errMsgGen(tracer)
    if ERR_result:
        return ERR_result

    functions=list(set(j for i in exprs for j in i.atoms(AppliedUndef)))
    functions.sort(key=lambda i:i.__repr__())
    tg=yield list(map(str,functions))
    target=[functions[i] for i in range(len(functions)) if tg[i]]

    result=sympy.dsolve(exprs,target)
    yield result