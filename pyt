from tree_sitter_languages import get_language, get_parser
import os

def detect_language(file_path):
    if file_path.endswith(".py"):
        return "python"
    elif file_path.endswith(".c") or file_path.endswith(".h"):
        return "c"
    return None

def get_function_name(node, lang):
    if lang == "python" and node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        return name_node.text.decode() if name_node else None
    elif lang == "c" and node.type == "function_definition":
        decl = node.child_by_field_name("declarator")
        if decl:
            id_node = decl.child_by_field_name("declarator")
            return id_node.text.decode() if id_node else None
    return None

def get_function_calls(node, lang):
    calls = set()
    def walk(n):
        if lang == "python" and n.type == "call":
            func = n.child_by_field_name("function")
            if func:
                calls.add(func.text.decode())
        elif lang == "c" and n.type == "call_expression":
            func = n.child_by_field_name("function")
            if func:
                calls.add(func.text.decode())
        for child in n.children:
            walk(child)
    walk(node)
    return list(calls)

def extract_functions_and_calls(tree, lang):
    root = tree.root_node

    def walk(node):
        results = []
        if node.type == "function_definition":
            func_name = get_function_name(node, lang)
            if func_name:
                called = get_function_calls(node, lang)
                results.append((func_name, called))
        for child in node.children:
            results.extend(walk(child))
        return results

    return walk(root)

def parse_file(file_path):
    lang = detect_language(file_path)
    if not lang:
        print(f"Unsupported file type: {file_path}")
        return

    parser = get_parser(lang)
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    tree = parser.parse(bytes(code, "utf8"))
    results = extract_functions_and_calls(tree, lang)

    output_path = os.path.splitext(file_path)[0] + "_functions.txt"
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"Results for {file_path} ({lang})\n")
        out.write("-" * 40 + "\n")
        for func, calls in results:
            out.write(f"Function: {func}\n")
            if calls:
                out.write(f"  Calls: {', '.join(calls)}\n")
            else:
                out.write("  Calls: None\n")
            out.write("\n")

    print(f"Results saved to: {output_path}")

# === MAIN ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <source-file>")
    else:
        parse_file(sys.argv[1])