from pathlib import Path
from helpers import sanitize_filename, build_tree, render_tree
from collections import defaultdict

label_to_filepath = {}
keyword_hits = defaultdict(list)
keyword_pages = []

def write_log_page(file_path, source_label, keywords, output_dir):
    out_name = sanitize_filename(Path(source_label)) + ".html"
    out_path = output_dir / out_name
    label_to_filepath[source_label] = file_path

    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"""
                    <!DOCTYPE html>
                    <html lang='en'>
                    <head>
                <meta charset='UTF-8'><title> {source_label}</title>
                <style>
                    body
                    {{ font-family: monospace; background: #1e1e1e; color: #dcdcdc; padding: 20px; }}
                    pre 
                    {{ white-space: pre-wrap; word-wrap: break-word; background: #2e2e2e; padding: 10px; border-radius: 5px; }}
                    a
                    {{ color: #4fc3f7; }}
                </style></head><body>
                <p><strong>File:</strong> {source_label}</p><pre>
            """)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                for lineno, line in enumerate(log_file,1):
                    safe_line = line.replace("<", "&lt;").replace(">", "&gt;")
                    f.write(safe_line)
                    for keyword in keywords:
                        if keyword.lower() in line.lower():
                            keyword_hits[keyword].append((source_label, lineno, line.strip()))

            f.write("</pre><br><a href='../index.html'>&larr; Back to index</a></body></html>")
        return out_name
    except Exception as e:
        print(f"Failed to write {source_label}: {e}")
        return None


def generate_index_html(grouped_entries):
    with open("index.html", 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html><html lang='en'><head>
            <meta charset='UTF-8'><title>Log Index</title>
            <style>
                body { font-family: sans-serif; background: #1e1e1e; color: #ffffff; padding: 20px; }
                a { color: #4fc3f7; text-decoration: none; }
                a:hover { text-decoration: underline; }
                summary { cursor: pointer; }
                h2 { margin-top: 30px; border-bottom: 1px solid #555; }
                ul { list-style-type: none; padding-left: 20px; }
            </style></head><body><h1>Log Index</h1>
        """)

        total_files = sum(len(entries) for entries in grouped_entries.values())
        f.write(f"<p>Total Files: {total_files}</p>\n")

        for top_folder, entries in grouped_entries.items():
            if top_folder in {".", "root"}:
                f.write("<h2>Root Files</h2>\n")
                tree = build_tree(entries)
                f.write(render_tree(tree))
            else:
                f.write(f"<details open><summary><h2>{top_folder}/</h2></summary>")
                tree = build_tree(entries)
                f.write(render_tree(tree))
                f.write("</details>")

        f.write("</body></html>")


def generate_keyword_pages(output_dir):
    for keyword, matches in keyword_hits.items():
        fname = f"keyword_{keyword}.html"
        keyword_pages.append(fname)

        unique_labels = {label for label, _, _ in matches}

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html><html lang='en'><head>
                <meta charset='UTF-8'><title>Keyword: {keyword}</title>
                <style>
                    body {{ font-family: sans-serif; background: #1e1e1e; color: #ffffff; padding: 20px; }}
                    a {{ color: #4fc3f7; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    pre {{ background: #2e2e2e; padding: 10px; border-radius: 5px; }}
                </style></head><body>
                <h1>Keyword: '{keyword}'</h1>
                <p>Unique files: {len(unique_labels)}</p><ul>
            """)

            # Group by file
            grouped = defaultdict(list)
            for label, lineno, line_content in matches:
                grouped[label].append((lineno, line_content))

            for label in sorted(grouped):
                page_name = sanitize_filename(Path(label)) + ".html"
                f.write(f"<li><a href='log_pages/{page_name}' target='_blank'>{label}</a>\n")
                f.write("<pre>\n")
                for lineno, content in grouped[label]:
                    f.write(f"Line {lineno}: {content}\n")
                f.write("</pre></li>\n")

            f.write("</ul></body></html>")

