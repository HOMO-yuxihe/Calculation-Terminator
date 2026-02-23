import sympy
import matplotlib.pyplot as plt
from io import BytesIO

plt.rcParams['text.usetex']=False
plt.rcParams['mathtext.fontset']='cm'
plt.rcParams['text.latex.preamble']=r'\usepackage{bm}'  # 或 \usepackage{amsmath}
plt.rcParams['svg.fonttype']='path'
def latex2svg(tex:str,font_size=12):
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
    expression=sympy.parse_expr(expr)
    return sympy.latex(expression,mode='plain')

if __name__ == '__main__':
    pass
    # text = r'$x^2+y^2=z^2$'
    # print(latex_formula2svg(text,font_size=12))
    expr='x**2+y**2-z**2'
    tex=expr2latex(expr)
    print(tex)
    print(latex2svg(tex))