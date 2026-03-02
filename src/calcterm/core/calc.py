import sympy,keyword
from sympy.core.function import AppliedUndef
from sympy.core.assumptions_generated import defined_facts
from typing import Dict,List, Tuple,Union
from .struct_template import *
from .exception_parser import parse_expr,syntaxErrTranslate

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
    'series':sympy.series,
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
    'Function':sympy.Function,
    'Symbol':sympy.Symbol,

    'solve':sympy.solve
}

VALID_FUNCTION_ASSUMPTIONS = {
        'real', 'imaginary', 'complex',
        'finite', 'infinite',
        'continuous', 'differentiable', 'analytic',
        'monotonic', 'increasing', 'decreasing',
        'even', 'odd', 'periodic',
        'commutative'
}

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

def localDictGen(namespace:Namespace):# -> dict:
    local={}
    for i in namespace['variables']:
        local[i['id']]=sympy.Symbol(i['name'],**i['assumptions'])
    for i in namespace['functions']:
        local[i['id']]=sympy.Function(i['name'],**i['assumptions'])
    return local

def evalf(exp:str,digit:int):
    result=sympy.simplify(parse_expr(exp))
    return str(result.evalf(digit))

def simplify(exp:str):
    return str(sympy.simplify(parse_expr(exp)))

def calc(exp:str,namespace:Namespace)->Tuple[str,Tuple[str,Union[None,Tuple[str,str]]]]:
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
    result=[None,None]
    if not exp.strip():
        return [None,('错误','表达式不能为空')]
    local=localDictGen(namespace)
    try:
        result[0]=str(parse_expr(exp,local_dict=local,global_dict=glob)).replace('log','ln')
    except SyntaxError as e:
        result[1]=('语法错误',syntaxErrTranslate(e))
    except Exception as e:
        result[1]=('错误',repr(e))
    
    return result

def lagrange(lm:List[str],tg:str,namespace:Namespace)->Tuple[str,Tuple[str,Union[None,Tuple[str,str]]]]:
    if not tg.strip():
        return [None,('错误','目标函数不能为空')]
    lambdas=[sympy.Symbol(f'λ_{i}',real=1) for i in range(1,len(lm)+1)]
    local=localDictGen(namespace)
    result=[None,None]
    
    lm_exprs:List[sympy.Expr]=[]
    for i,j in enumerate(lm):
        try:
            lm_exprs.append(parse_expr(j,global_dict=glob,local_dict=local))
        except SyntaxError as e:
            result[1]=('语法错误',f'第{i+1}条约束条件存在语法错误:'+syntaxErrTranslate(e))
            return result
        except Exception as e:
            result[1]=('错误',f'第{i+1}条约束条件解析错误:'+repr(e))
            return result

    try:
        tg_expr:sympy.Expr=parse_expr(tg,global_dict=glob,local_dict=local)
    except SyntaxError as e:
        result[1]=('语法错误','目标函数表达式存在语法错误'+syntaxErrTranslate(e))
        return result
    except Exception as e:
        result[1]=('解析错误','目标函数表达式解析出错:'+repr(e))
        return result

    variables=list(set([j for i in lm_exprs+[tg_expr] for j in i.free_symbols]))+lambdas

    Lag=tg_expr
    for i,lamda in enumerate(lambdas):
        Lag+=lamda*lm_exprs[i]
    expr=[sympy.diff(Lag,i) for i in variables]
    try:
        solves=sympy.solve(expr)
    except Exception as e:
        result[1]=('求解错误','求解出错:'+repr(e))
        return result

    if type(solves)==dict:solves=[solves]
    result[0]=[]
    for i in solves:
        solve=sympy.simplify(Lag.subs(i))
        i={str(a):str(b) for a,b in i.items()}
        i['result']=str(solve)
        result[0].append(i)
    return result

def smartsolver(expr:List[str],namespace:Namespace):
    if not expr:
        return [None,('错误','待求解方程组为空')]
    result=[None,None]
    local=localDictGen(namespace)

    exprs=[]
    for i,j in enumerate(expr):
        try:
            exprs.append(parse_expr(j,global_dict=glob,local_dict=local))
        except SyntaxError as e:
            return [None,('语法错误',f'第{i+1}条表达式存在语法错误:'+syntaxErrTranslate(e))]
        except Exception as e:
            return [None,('解析错误',f'第{i+1}条表达式解析错误:'+repr(e))]

    symbols=list(set(j for i in exprs for j in i.free_symbols))
    if not symbols:
        return [None,('错误','没有待求解变量')]
    symbols.sort(key=lambda i:i.name)
    tg=yield list(map(str,symbols))
    target=[symbols[i] for i in range(len(symbols)) if tg[i]]

    nlsolve=lambda:[{symbol:i[index] for index,symbol in enumerate(target)}
                for i in list(sympy.nonlinsolve(exprs,*target))]
    try:
        result=sympy.solve(exprs,*target,dict=True)
    except NotImplementedError:
        try:
            result[0]=nlsolve()
        except NotImplementedError:
            return [None,('不支持','抱歉，程序暂不支持该方程组')]
        except Exception as e:
            return [None,('求解错误','方程组求解出错:'+repr(e))]
    except Exception as e:
        return [None,('求解错误','方程组求解出错:'+repr(e))]
    if result[0]==[]:
        result=nlsolve()
    print(result)
    yield [{str(j):str(k) for j,k in i.items()} for i in result[0]]

def dsolver(expr:List[str],namespace:Namespace,ics:List[str]=[]):
    if not expr:
        return [None,('错误','待求解方程组为空')]
    local=localDictGen(namespace)

    exprs=[]
    for i,j in enumerate(expr):
        try:
            exprs.append(parse_expr(j,global_dict=glob,local_dict=local))
        except SyntaxError as e:
            return [None,('语法错误',f'第{i+1}条表达式存在语法错误:'+syntaxErrTranslate(e))]
        except Exception as e:
            return [None,('解析错误',f'第{i+1}条表达式解析错误:'+repr(e))]

    icss={}
    for i,j in enumerate(ics):
        if not (j:=j.strip()):
            continue
        if (cnt:=j.count('='))!=1:
            return [None,('格式错误',f'第{i+1}条初始条件有{cnt}个等号。\n每个初始条件必须有1个等号。')]

        try:
            lhs,rhs=map(lambda x:parse_expr(x,local_dict=local,global_dict=glob),j.split('='))
        except SyntaxError as e:
            return [None,('语法错误',f'第{i+1}条初始条件存在语法错误:'+syntaxErrTranslate(e))]
        except Exception as e:
            return [None,('解析错误',f'第{i+1}条初始条件解析错误:'+repr(e))]

        if not isinstance(lhs,(AppliedUndef,sympy.Derivative,sympy.Subs)):
            return [None,('格式错误',f'第{i+1}条初始条件格式错误。\n必须使用形如f(x)=y的形式定义初始条件')]
        icss[lhs]=rhs

    functions=list(set(j for i in exprs for j in i.atoms(AppliedUndef)))
    if not functions:
        return [None,('错误','没有待求解函数')]
    functions.sort(key=lambda i:i.__repr__())

    tg=yield list(map(str,functions))
    target=[functions[i] for i in range(len(functions)) if tg[i]]

    if len(exprs)==1 and len(target)==1:
        exprs=exprs[0]
        target=target[0]

    try:
        result:Union[List[sympy.Eq],List[List[sympy.Eq]]]=sympy.dsolve(exprs,target,ics=icss)
    except Exception as e:
        return [None,('求解错误','方程组求解出错:'+repr(e))]

    res:List[Dict[AppliedUndef,sympy.Expr]]=...
    if isinstance(result,sympy.Eq):
        res=[{result.lhs:result.rhs}]
    elif isinstance(result[0],sympy.Eq):
        res=[{i.lhs:i.rhs for i in result}]
        if len(res[0])!=len(result):
            res=[{i.lhs:i.rhs} for i in result]
    else:
        res=[{j.lhs:j.rhs for j in i} for i in result]
    yield [None,[{str(j):str(k) for j,k in i.items()} for i in res]]

def is_assumption(assump:str):
    return assump in defined_facts

def is_function_assumption(assump:str):
    return assump in VALID_FUNCTION_ASSUMPTIONS
