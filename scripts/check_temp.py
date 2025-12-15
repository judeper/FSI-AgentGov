from pathlib import Path
import hashlib

TEMP_DIR = Path("temp")
REPO_DIR = Path(".")

# Suspected mappings based on naming
MAPPING = {
    "FAQ.md": "docs/reference/faq.md",
    "Glossary.md": "docs/reference/glossary.md",
    "Implementation-Checklist.md": "docs/getting-started/checklist.md",
    "Quick-Start-Guide.md": "docs/getting-started/quick-start.md",
    "RACI-Matrix.md": "docs/reference/raci-matrix.md",
    "README.md": "docs/index.md", # Checking if it matches index.md, root README is too small
    "Regulatory-Mappings.md": "docs/reference/regulatory-mappings.md",
    "Zones-Overview.md": "docs/getting-started/zones.md"
}

def get_hash(path):
    if not path.exists(): return None
    return hashlib.md5(path.read_bytes()).hexdigest()

def check_files():
    print("Checking temp files against repository...")
    
    for temp_name, repo_path_str in MAPPING.items():
        temp_path = TEMP_DIR / temp_name
        repo_path = REPO_DIR / repo_path_str
        
        if not temp_path.exists():
            print(f"[MISSING] {temp_name} not found in temp.")
            continue
            
        temp_hash = get_hash(temp_path)
        repo_hash = get_hash(repo_path)
        
        print(f"\nFile: {temp_name}")
        print(f"  Mapping to: {repo_path_str}")
        
        if not repo_path.exists():
            print(f"  [ERROR] Repo file not found: {repo_path_str}")
            # Try finding it elsewhere?
            continue
            
        if temp_hash == repo_hash:
            print("  [MATCH] Content is identical.")
        else:
            print("  [DIFF] Content differs.")
            print(f"  Temp Size: {temp_path.stat().st_size}")
            print(f"  Repo Size: {repo_path.stat().st_size}")
            
            # Special check for README
            if temp_name == "README.md":
                root_readme = REPO_DIR / "README.md"
                root_hash = get_hash(root_readme)
                if temp_hash == root_hash:
                     print("  [MATCH] Matches root README.md (Unexpected based on size).")
                else: 
                     print(f"  [INFO] Root README size: {root_readme.stat().st_size}")

if __name__ == "__main__":
    check_files()
