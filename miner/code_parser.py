import ast
import re

def extract_python_methods(source_code: str) -> list[str]:
    method_names = []
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not (node.name.startswith('__') and node.name.endswith('__')):
                method_names.append(node.name)

    return method_names

def extract_java_methods(source_code: str) -> list[str]:
    pattern = r'(?:public|protected|private|static|final|abstract|\s)*\s+[\w\<\>\[\]]+\s+(\w+)\s*\('
    matches = re.findall(pattern, source_code)
    reserved_words = {'if', 'for', 'while', 'switch', 'catch', 'return', 'new', 'synchronized'}
    return [m for m in matches if m not in reserved_words]