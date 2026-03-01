import sympy
from sympy.core.numbers import One
import matplotlib.pyplot as plt
from io import BytesIO

from calcterm.core.exception_parser import parse_expr

plt.rcParams['text.usetex']=False
plt.rcParams['mathtext.fontset']='cm'
plt.rcParams['text.latex.preamble']=r'\usepackage{bm}'  # 或 \usepackage{amsmath}
plt.rcParams['svg.fonttype']='path'

def remove_mul_1(node:sympy.Expr):
    if not node.args:
            return node
    new_args=[]
    if isinstance(node,sympy.Mul):
        for arg in node.args:
            processed_arg=remove_mul_1(arg)
            if not isinstance(processed_arg,One):
                new_args.append(processed_arg)
    else:
        new_args=[remove_mul_1(arg) for arg in node.args]
    if isinstance(node,sympy.Mul) and len(new_args)==1:
        return new_args[0]
    else:
        try:
            return node.func(*new_args,evaluate=False)
        except ValueError:
            return node.func(*new_args)

def latex2svg(tex:str,font_size=12):
    if not tex.strip():return ''
    text=f'${tex}$'
    plt.rcParams['font.size']=font_size
    fig,ax = plt.subplots()
    txt = ax.text(0.5,0.5,text,ha='center',va='center',transform=ax.transAxes)
    ax.axis('off')
    fig.canvas.draw()
    bbox = txt.get_window_extent(renderer=fig.canvas.get_renderer())
    fig.set_size_inches(bbox.width/fig.dpi,bbox.height/fig.dpi)

    bin=BytesIO()
    fig.savefig(bin,format='svg',bbox_inches=None,pad_inches=0,transparent=True)
    bin.seek(0)
    result = bin.getvalue()
    bin.close()
    plt.close(fig)
    # plt.show()
    return result.decode('utf-8')

def expr2latex(expr:str):
    if not expr.strip():return ''
    expression=remove_mul_1(parse_expr(expr,evaluate=False))
    return sympy.latex(expression,mode='plain')

if __name__ == '__main__':
    pass
    # text = r'$x^2+y^2=z^2$'
    # print(latex_formula2svg(text,font_size=12))
    expr='2*4*6'
    tex=expr2latex(expr)
    print(tex)
    # print(latex2svg(tex))