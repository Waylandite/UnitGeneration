# complete focal method   焦点方法
# the focal class name   焦点类名
# the fields in the focal class     类中字段
# signatures of all methods defined in the focal class   类中定义的其他函数签名

# The definition of the dep methods invoked by the focal method

import re

import javalang


# 定义用于存储函数签名和函数体的类
class JavaMethod:
    def __init__(self, signature,name, body):
        self.signature = signature
        self.name = name
        self.body = body

    def __str__(self):
        return f"Method signature:\n{self.signature}\nMethod body:\n{self.body}\n"

# 定义用于存储类签名和字段的类
class JavaClass:
    def __init__(self, full_class_definition, class_name, fields,methods):
        self.full_class_definition = full_class_definition
        self.class_name = class_name
        self.fields = fields
        self.methods = methods

    def __str__(self):
        return f"Full class definition:  {self.full_class_definition}\n"


# Java类定义的正则表达式，包括extends和implements
class_pattern = (r'\b(public|private|protected)?\s*'   # 可选的访问修饰符
           r'(abstract|final)?\s*'              # 可选的类修饰符
           r'class\s+(\w+)\s*'                  # 类名
           r'(?:\s+extends\s+(\w+))?'           # 可选的 extends 父类
           r'(?:\s+implements\s+([\w\s,]+))?'   # 可选的 implements 接口列表
           r'\s*\{')                            # 花括号起始

# 正则表达式匹配方法定义（不包括方法体）
method_pattern = r'(public|private|protected)?\s+[a-zA-Z0-9_\[\]<>]+(\s*<[a-zA-Z0-9_,\s<>]*>)?\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(throws\s+[a-zA-Z0-9_,\s]+)?\s*\{'


def extract_body(content, method_start_pos):
    """
    从给定的起始位置开始，匹配整个方法体，包括大括号的匹配。
    """
    brace_stack = []
    method_body = ""
    i = method_start_pos

    # 从起始位置开始遍历字符
    while i < len(content):
        char = content[i]
        method_body += char

        # 遇到左大括号，压栈
        if char == '{':
            brace_stack.append('{')
        # 遇到右大括号，出栈
        elif char == '}':
            brace_stack.pop()

        # 当栈为空时，表示函数体已经完整匹配
        if not brace_stack:
            break

        i += 1

    return method_body

def extract_class_definition(content,pattern):
    """ 提取类的完整定义 """
    matches = re.finditer(pattern, content)
    class_list=[]
    for match in matches:
        class_signature = match.group(0)
        access_modifier = match.group(1)
        class_modifier = match.group(2)
        class_name = match.group(3)
        extends_class = match.group(4)  # 可能是None
        implements_interfaces = match.group(5)  # 可能是None
        # 获取类完整定义
        class_body=extract_body(content, match.end() - 1)
        class_signature = class_signature.rstrip('{')
        class_list.append({
            'class_signature': class_signature,
            'class_name': class_name,
            'class_body': class_body
        })
    return class_list


def extract_fields(content, method_positions):
    """提取剩余部分并将其拼接为一个字符串"""

    # 排除所有方法签名和方法体，将剩余部分拼接起来
    remaining_content = []
    last_pos = 0

    # 方法位置按起始位置升序排序
    for start, end in sorted(method_positions):
        # 将上一个方法结束位置到下一个方法开始位置之间的部分保留下来
        remaining_content.append(content[last_pos:start])
        last_pos = end

    # 添加最后一个方法后剩余的内容
    remaining_content.append(content[last_pos:])

    # 将所有剩余部分拼接起来
    field_content = ''.join(remaining_content)

    # 1. 去除收尾的大括号
    field_content = field_content.strip().lstrip('{').rstrip('}')

    # 2. 去除以 @ 开头的注解行
    lines = field_content.splitlines()
    cleaned_lines = [line for line in lines if not line.strip().startswith('@')]

    # 3. 去除多余的空格（每一行去除首尾空格后重新拼接）
    cleaned_content = '\n'.join(line.strip() for line in cleaned_lines if line.strip())

    return cleaned_content
def extract_method(content,pattern):
    # 匹配方法签名
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    # 创建一个列表，用于存储所有方法对象
    methods_list = []
    method_positions = []
    # 遍历所有找到的方法定义
    for match in matches:
        method_signature = match.group(0)
        method_name = match.group(3)
        method_start_pos = match.end() - 1  # 方法定义后面的位置
        # 提取方法体
        method_body = extract_body(content, method_start_pos)
        # 去掉method_signature最后一个用于匹配的{
        method_signature = method_signature.rstrip('{')
        # 记录方法的起始和结束位置，以便后续从 content 中删除方法部分
        method_end_pos = method_start_pos + len(method_body)
        method_positions.append((match.start(), method_end_pos))
        # 创建一个方法对象并添加到列表中
        method = JavaMethod(method_signature, method_name,method_body)
        methods_list.append(method)
    # 移除所有方法签名和方法体，提取剩余部分作为类的字段
    fields_content = extract_fields(content, method_positions)
    return methods_list, fields_content


if __name__ == '__main__':
    file_path = r'D:\OneDrive\Work\04Experiment\UnitGeneration\project\eladmin-tools\src\main\java\me\zhengjie\service\impl\AliPayServiceImpl.java'
    focal_method = JavaMethod("public String toPayAsPc(AlipayConfig alipay, TradeVo trade) throws Exception","toPayAsPc","")

    # 打开文件并读取内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 提取类的完整定义和类名
    class_Dicts = extract_class_definition(content,class_pattern)
    Class_List=[]
    focal_classIndex=-1
    for class_dict in class_Dicts:
        print(class_dict)
        # 提取类中方法部分
        methods_list,fields_content =extract_method(class_dict["class_body"],method_pattern)
        for method in methods_list:
            print(method)
            print("=" * 50)
            if(focal_method.name == method.name):
                focal_classIndex =len(Class_List)
                focal_method.body = method.body

        print(fields_content)
        java_class = JavaClass(class_dict["class_signature"], class_dict["class_name"], fields_content, methods_list)
        Class_List.append(java_class)
    if focal_classIndex !=-1:
        # focal_method     focal_classIndex   Class_List
        print("structure is over")
        focal_conent=focal_method.signature + focal_method.body
        focal_conent=Class_List[focal_classIndex].full_class_definition+"{"+focal_conent+"}"
        print(focal_conent)
        tree = javalang.parse.parse(focal_conent)
        print(tree)
    else:
        print("focal method is not in the content ")


