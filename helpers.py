def sanitize_filename(name):
    if hasattr(name, "parts"):
        return "_".join(name.parts).replace(".", "_").replace("/", "_").replace(" ", "_")
    return str(name).replace(".", "_").replace("/", "_").replace(" ", "_")

def build_tree(entries):
    tree = {}
    for path, link in entries:
        parts = path.split("/")
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = link
    return tree

def render_tree(tree):
    html = "<ul>"
    for name, value in sorted(tree.items()):
        if isinstance(value, dict):
            html += f"<li><details><summary>{name}/</summary>{render_tree(value)}</details></li>"
        else:
            html += f"<li><a href='log_pages/{value}' target='_blank'>{name}</a></li>"
    html += "</ul>"
    return html
