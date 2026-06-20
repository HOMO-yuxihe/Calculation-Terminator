from sympy import FallingFactorial
from sympy.functions.combinatorial.factorials import binomial

class LatexBinomial(binomial):
    def _latex(self, printer):
        n_expr = printer._print(self.args[0])
        k_expr = printer._print(self.args[1])
        # 输出 C_{n}^{k}
        return rf"\mathrm{{C}}_{{{n_expr}}}^{{{k_expr}}}"

class LatexFallingFactorial(FallingFactorial):
    def _latex(self, printer):
        n_expr = printer._print(self.args[0])
        k_expr = printer._print(self.args[1])
        # 输出 A_{n}^{k}
        return rf"\mathrm{{A}}_{{{n_expr}}}^{{{k_expr}}}"