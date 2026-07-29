import os
import re

def remove_java_comments(content):
    # Remove multi-line comments /* ... */
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove single-line comments // ...
    content = re.sub(r'//.*', '', content)
    return content

def process_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = remove_java_comments(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    java_dir = r'c:\Users\NEHITH\Documents\java fenrir\src\main\java\com\aetherflow'
    
    for filename in os.listdir(java_dir):
        if filename.endswith('.java'):
            file_path = os.path.join(java_dir, filename)
            print(f'Processing: {filename}')
            process_java_file(file_path)
    
    print('Done!')

if __name__ == '__main__':
    main()
