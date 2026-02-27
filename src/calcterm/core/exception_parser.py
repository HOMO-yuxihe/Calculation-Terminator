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