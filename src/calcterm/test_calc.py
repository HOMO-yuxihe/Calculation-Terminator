from core.calc import *

# dsolve=dsolver(['diff(diff(f(x)))+f(x)-g(x)',
#                 'diff(diff(g(x)))-f(x)+g(x)'],
#                 [{'id':'x','name':'x','assumptions':{}},
#                  {'id':'a','name':'a','assumptions':{}},
#                  {'id':'b','name':'b','assumptions':{}}],
#                 [{'id':'f','name':'f','assumptions':{}},
#                  {'id':'g','name':'g','assumptions':{}}])
dsolve=dsolver(['diff(diff(f(x)))-x'],
               [{'id':'x','name':'x','assumptions':{}}],
               [{'id':'f','name':'f','assumptions':{}}],
               ['f(1)=1','f(0)-1=0'])
print(dsolve.__next__())
sol=dsolve.send([1])
print(sol)