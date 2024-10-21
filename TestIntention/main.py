import javalang
from javalang.tree import MethodDeclaration

if __name__ == '__main__':
    fd = open(
        r"D:\OneDrive\Work\04Experiment\UnitGeneration\TestIntention\test.java",
        "r", encoding="utf-8")  # 读取Java源代码
    tree = javalang.parse.parse(fd.read())  # 根据源代码解析出一颗抽象语法树
    # 这里返回了一个javalang.tree.CompilationUnit类型，表示整颗抽象语法树
    # print(tree)

    # for i in range(0, len(tree.children)):
    #     print(tree.children[i])
    #     print("*"*50)
    # CompilationUnit（编译单元）的children是一个数组，由三个元素构成：[包声明,Import声明数组,类声明数组]

    # 类声明数组是一个包含ClassDeclaration的List，包含了annotations和body

    # for i in tree.children[2][0].body:
    #     print(i)
    #     print("*"*50)
    # body也是一个数组，包含不同的声明，可以有FieldDeclaration、MethodDeclaration、LocalVariableDeclaration等

    # 函数声明MethodDeclaration

    for i in tree.children[2][0].body:
        if(type(i)==MethodDeclaration):
            # print(i)
            method=i

    for i in method.body:
        print(i)
        print("*" * 50)
    # body也是一个数组，根据代码顺序确定里面的元素。 body里面的元素就是表达式语句StatementExpression等等

#     通过此库，我们构建了一个java程序的AST


