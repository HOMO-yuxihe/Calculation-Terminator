import enum
from statistics import variance
import sympy,keyword
from typing import Dict,List,TypedDict

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

    'Integer':sympy.Integer,
    'Float':sympy.Rational,
    # 'Function':sympy.Function,
    # 'Symbol':sympy.Symbol,

    'solve':sympy.solve
}

class Variable(TypedDict):
    id:str
    name:str
    assumptions:Dict[str,bool]

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

def localDictGen(vars:List[Variable]):
    local={}
    for i in vars:
        local[i['id']]=sympy.Symbol(i['name'],**i['assumptions'])
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

def calc(exp:str,vars:List[Variable],ifeval:bool=False,digit=15) -> str:
    '''
    parse2:解析Sympy表达式
    
    :param exp: 表达式
    :type exp: str
    :param vars: 变量字典(变量标识符名:变量显示名)
    :type vars: dict
    :param ifeval: 输出数值形式
    :type ifeval: bool
    :param digit: 有效数字位数
    :return: 表达式结果
    :rtype: str
    '''
    tracer=SymbolTracer()
    local=localDictGen(vars)
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

def lagrange(lm:List[str],tg:str,vars:List[Variable]):
    lambdas=[sympy.Symbol(f'λ_{i}',real=1) for i in range(1,len(lm)+1)]
    tracer=SymbolTracer()
    local=localDictGen(vars)
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

def solver(expr:List[str],vars:List[Variable]):
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

if __name__ == '__main__':
    # x,y=sympy.symbols('x y',real=1,positive=(1,1))
    # lagrange([4*x+y+x*y-5],16*x**2+y**2,{x:'x',y:'y'})
    # lagrange(['4*x+y+x*y-5'],'16*x**2+y**2',
    #          [{'id':'x','name':'x','assumptions':{'real':True}},
    #           {'id':'y','name':'y','assumptions':{'real':True}}])
    # print(parse2('abc'))
    # print(solver(['x+y-6','x*y-5'],['x','y'],
    #              [{'id':'x','name':'x','assumptions':{'real':True}},
    #               {'id':'y','name':'y','assumptions':{'real':True}}]))
    # solve=solver(['(x-5)*(x-2.5)','y-1'],
    #              [{'id':'x','name':'x','assumptions':{'integer':True}},
    #               {'id':'y','name':'y','assumptions':{'integer':True}}])
    # print(solve.__next__())
    # print(solve.send([0,1]))
    # solve=smartsolver(['x**3 + y - 9','x + y**2 - 5'],
    #             [{'id':'x','name':'x','assumptions':{'real':1}},
    #              {'id':'y','name':'y','assumptions':{'real':1}}])
    # print(solve.__next__())
    # print(solve.send([1,1]))
    pass