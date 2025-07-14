import bs4
from html_to_markdown import convert_to_markdown
from rich import print
import requests
import mistune

url = 'https://www.tutorialspoint.com/python/python_vs_cpp.htm'

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    html_content = response.text
except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
    html_content = None

html = ""
if html_content:
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    main_content = soup.find(id='mainContent')
    if main_content:
        html = str(main_content)
    else:
        print("Could not find element with id 'mainContent'.")

markdown = convert_to_markdown(html)

markdown_ast = mistune.create_markdown(renderer=mistune.AstRenderer())(markdown)

# Helper to flatten text from paragraph/list item blocks
def flatten_text(block):
    if isinstance(block, str):
        return block
    elif isinstance(block, list):
        return ''.join(flatten_text(child) for child in block)
    elif isinstance(block, dict):
        if 'text' in block:
            return block['text']
        elif 'children' in block:
            return flatten_text(block['children'])
    return ''

# Process AST into structured sections
structured_data = {
    "title": "",
    "summary": "",
    "sections": [],
    "table": "",
    "key_takeaways": []
}

current_section = None

for block in markdown_ast:
    if block["type"] == "heading":
        level = block["level"]
        heading_text = flatten_text(block["children"])
        
        if level == 1 and not structured_data["title"]:
            structured_data["title"] = heading_text
        elif level == 2 or level == 3:
            if current_section:
                structured_data["sections"].append(current_section)
            current_section = {
                "heading": heading_text,
                "summary": "",
                "bullets": [],
                "code": "",
                "code_explanation": ""
            }
    elif current_section:
        if block["type"] == "paragraph":
            text = flatten_text(block["children"])
            current_section["summary"] += text + "\n"
        elif block["type"] == "list":
            for item in block["children"]:
                bullet_text = flatten_text(item["children"])
                current_section["bullets"].append(bullet_text)
        elif block["type"] == "block_code":
            current_section["code"] += block["text"] + "\n"
        elif block["type"] == "table":
            table_header = [flatten_text(h["children"]) for h in block["header"]]
            table_rows = [
                [flatten_text(cell["children"]) for cell in row]
                for row in block["cells"]
            ]
            table_md = "| " + " | ".join(table_header) + " |\n"
            table_md += "| " + " | ".join("---" for _ in table_header) + " |\n"
            for row in table_rows:
                table_md += "| " + " | ".join(row) + " |\n"
            structured_data["table"] = table_md

if current_section:
    structured_data["sections"].append(current_section)

print(markdown)
print("\n"*5)
print(structured_data)