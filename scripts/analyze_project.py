import os
import json
import collections

def get_languages(root_dir):
    ext_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.html': 'HTML',
        '.css': 'CSS',
        '.go': 'Go',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.rs': 'Rust',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.yml': 'YAML',
        '.yaml': 'YAML',
    }
    
    stats = collections.defaultdict(int)
    total_size = 0
    
    exclude_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.agent', '.gemini'}
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in ext_map:
                lang = ext_map[ext]
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                    stats[lang] += size
                    total_size += size
                except OSError:
                    continue
                    
    if total_size == 0:
        return {}
        
    return {lang: round((size / total_size) * 100, 2) for lang, size in stats.items()}

def get_dependencies(root_dir):
    deps = []
    
    # Node.js
    pkg_json_path = os.path.join(root_dir, 'package.json')
    if os.path.exists(pkg_json_path):
        try:
            with open(pkg_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                for name, ver in all_deps.items():
                    # Attempt to find license in node_modules
                    license = "Unknown"
                    node_modules_pkg = os.path.join(root_dir, 'node_modules', name, 'package.json')
                    if os.path.exists(node_modules_pkg):
                        try:
                            with open(node_modules_pkg, 'r', encoding='utf-8') as nf:
                                ndata = json.load(nf)
                                license = ndata.get('license', 'Unknown')
                                if isinstance(license, dict):
                                    license = license.get('type', 'Unknown')
                        except:
                            pass
                    deps.append({"name": name, "version": ver, "license": license})
        except:
            pass
            
    # Python (requirements.txt)
    req_txt_path = os.path.join(root_dir, 'requirements.txt')
    if os.path.exists(req_txt_path):
        try:
            with open(req_txt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('==')
                        name = parts[0]
                        ver = parts[1] if len(parts) > 1 else "latest"
                        deps.append({"name": name, "version": ver, "license": "Check PyPI"})
        except:
            pass
            
    return deps

def get_tech_stack(root_dir, languages, deps):
    stack = []
    dep_names = {d['name'] for d in deps}
    
    if 'React' in dep_names or 'react' in dep_names:
        stack.append("React")
    if 'next' in dep_names:
        stack.append("Next.js")
    if 'vue' in dep_names:
        stack.append("Vue.js")
    if 'express' in dep_names:
        stack.append("Express.js")
    if 'django' in dep_names:
        stack.append("Django")
    if 'flask' in dep_names:
        stack.append("Flask")
    if 'tailwindcss' in dep_names:
        stack.append("Tailwind CSS")
    if 'typescript' in dep_names or 'TypeScript' in languages:
        stack.append("TypeScript")
        
    # Add generic language entries if no specific framework found
    for lang in languages:
        if lang not in stack:
            stack.append(lang)
            
    return list(set(stack))

def main():
    root_dir = os.getcwd()
    languages = get_languages(root_dir)
    dependencies = get_dependencies(root_dir)
    tech_stack = get_tech_stack(root_dir, languages, dependencies)
    
    result = {
        "tech_stack": tech_stack,
        "languages": languages,
        "dependencies": dependencies
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
