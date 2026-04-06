import os
import re

admin_dir = r"c:\Users\purni\Downloads\skillseed\frontend\lib\screens\dashboards\admin"

def fix_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Fix mounted
    content = re.sub(
        r'(if\s*\(response\.statusCode\s*==\s*200\)\s*\{)(\s*)(setState\()',
        r'\1\2if (!mounted) return;\n\2\3',
        content
    )
    
    content = re.sub(
        r'(setState\(\(\)\s*=>\s*_isLoading\s*=\s*false\);\s*\})',
        r'if (mounted) \1',
        content
    )
    
    # Fix ElevatedButton.icon -> ElevatedButton with Row
    def replace_button(match):
        # We need to extract icon, label, style, onPressed
        # Match groups might not be simple because of nesting, so let's use a simpler heuristic or manually replace in known files.
        pass
        
    with open(filepath, "w") as f:
        f.write(content)

for filename in os.listdir(admin_dir):
    if filename.endswith(".dart"):
        fix_file(os.path.join(admin_dir, filename))
