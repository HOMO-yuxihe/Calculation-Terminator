from typing import Dict,List,TypedDict

class Variable(TypedDict):
    id:str
    name:str
    assumptions:Dict[str,bool]

class UndefinedFunction(TypedDict):
    id:str
    name:str
    nargs:int
    assumptions:Dict[str,bool]

class LambdaFunction(TypedDict):
    id:str
    name:str
    args:List[Variable]
    expr:str
    assumptions:Dict[str,bool]