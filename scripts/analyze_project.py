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
        '.cc': 'C++',
        '.cxx': 'C++',
        '.hpp': 'C++',
        '.h': 'C/C++ Header',
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

    # Go (go.mod)
    go_mod_path = os.path.join(root_dir, 'go.mod')
    if os.path.exists(go_mod_path):
        try:
            with open(go_mod_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('require ('):
                        continue
                    if line.startswith('require'):
                        parts = line.split()
                        if len(parts) >= 3:
                            deps.append({"name": parts[1], "version": parts[2], "license": "Check pkg.go.dev"})
                    elif ' ' in line and not line.startswith(('module', 'go', 'replace', 'exclude', ')')):
                        parts = line.split()
                        if len(parts) >= 2:
                            deps.append({"name": parts[0], "version": parts[1], "license": "Check pkg.go.dev"})
        except:
            pass

    # Rust (Cargo.toml)
    cargo_toml_path = os.path.join(root_dir, 'Cargo.toml')
    if os.path.exists(cargo_toml_path):
        try:
            import re
            with open(cargo_toml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                dep_sections = re.findall(r'\[(?:dev-)?dependencies\](.*?)(?=\n\[|$)', content, re.DOTALL)
                for section in dep_sections:
                    for line in section.strip().split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                name, ver = line.split('=', 1)
                                deps.append({"name": name.strip(), "version": ver.strip().replace('"', ''), "license": "Check Crates.io"})
        except:
            pass

    # Java (pom.xml)
    pom_xml_path = os.path.join(root_dir, 'pom.xml')
    if os.path.exists(pom_xml_path):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(pom_xml_path)
            root = tree.getroot()
            ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
            for dep in root.findall('.//mvn:dependency', ns):
                group = dep.find('mvn:groupId', ns)
                artifact = dep.find('mvn:artifactId', ns)
                version = dep.find('mvn:version', ns)
                name = f"{group.text}:{artifact.text}" if group is not None and artifact is not None else "Unknown"
                ver = version.text if version is not None else "Managed"
                deps.append({"name": name, "version": ver, "license": "Check Maven Central"})
        except:
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(pom_xml_path)
                root = tree.getroot()
                for dep in root.findall('.//dependency'):
                    group = dep.find('groupId')
                    artifact = dep.find('artifactId')
                    version = dep.find('version')
                    name = f"{group.text}:{artifact.text}" if group is not None and artifact is not None else "Unknown"
                    ver = version.text if version is not None else "Managed"
                    deps.append({"name": name, "version": ver, "license": "Check Maven Central"})
            except:
                pass

    # C/C++ (CMakeLists.txt)
    cmake_path = os.path.join(root_dir, 'CMakeLists.txt')
    if os.path.exists(cmake_path):
        try:
            import re
            with open(cmake_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find find_package calls
                packages = re.findall(r'find_package\s*\(\s*(\w+)', content, re.IGNORECASE)
                for pkg in packages:
                    deps.append({"name": pkg, "version": "N/A", "license": "Check CMake/Repo"})
        except:
            pass

    # C/C++ (vcpkg.json)
    vcpkg_path = os.path.join(root_dir, 'vcpkg.json')
    if os.path.exists(vcpkg_path):
        try:
            with open(vcpkg_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for dep in data.get('dependencies', []):
                    name = dep if isinstance(dep, str) else dep.get('name', 'Unknown')
                    deps.append({"name": name, "version": "vcpkg", "license": "Check vcpkg"})
        except:
            pass
            
    return deps

def get_tech_stack(root_dir, languages, deps):
    stack = []
    dep_names = {d['name'].lower() for d in deps}
    
    # Web Frameworks & Libraries
    frameworks = {
        'react': 'React', 'next': 'Next.js', 'vue': 'Vue.js', 'express': 'Express.js',
        'django': 'Django', 'flask': 'Flask', 'tailwindcss': 'Tailwind CSS',
        'gin-gonic/gin': 'Gin (Go)', 'labstack/echo': 'Echo (Go)', 'gofiber/fiber': 'Fiber (Go)',
        'actix-web': 'Actix (Rust)', 'rocket': 'Rocket (Rust)', 'axum': 'Axum (Rust)',
        'spring-boot': 'Spring Boot', 'quarkus': 'Quarkus', 'micronaut': 'Micronaut',
        'qt': 'Qt', 'boost': 'Boost', 'opencv': 'OpenCV', 'pcl': 'PCL', 'eigen': 'Eigen'
    }

    for dep, name in frameworks.items():
        if any(dep in d for d in dep_names):
            stack.append(name)

    if 'typescript' in dep_names or 'TypeScript' in languages:
        stack.append("TypeScript")
    if 'Java' in languages:
        stack.append("Java")
    if 'Go' in languages:
        stack.append("Go")
    if 'Rust' in languages:
        stack.append("Rust")
    if 'C++' in languages or 'C' in languages:
        stack.append("C/C++")
        
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
