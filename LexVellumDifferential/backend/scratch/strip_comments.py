import os
import re

def strip_comments(file_path):
    ext = os.path.splitext(file_path)[1]
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if ext == '.py':
        # Remove single line comments
        content = re.sub(r'#.*', '', content)
        # Remove triple quote docstrings (simplified)
        content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
    elif ext in ['.js', '.jsx', '.css']:
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove single-line comments (only for js/jsx)
        if ext != '.css':
            content = re.sub(r'//.*', '', content)

    # Clean up empty lines created by comment removal
    lines = [line for line in content.splitlines() if line.strip()]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def main():
    target_dirs = ['backend/app', 'frontend/src']
    for t_dir in target_dirs:
        abs_path = os.path.join(os.getcwd(), t_dir)
        for root, dirs, files in os.walk(abs_path):
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.css')):
                    print(f"Stripping comments from: {os.path.join(root, file)}")
                    strip_comments(os.path.join(root, file))

if __name__ == "__main__":
    main()
