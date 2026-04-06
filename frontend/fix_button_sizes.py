import os
import re

admin_dir = r"c:\Users\purni\Downloads\skillseed\frontend\lib\screens\dashboards\admin"

for filename in os.listdir(admin_dir):
    if filename.endswith(".dart"):
        filepath = os.path.join(admin_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()
            
        # Add minimumSize to override the global double.infinity style
        new_content = re.sub(
            r'(ElevatedButton\.styleFrom\()',
            r'\1minimumSize: const Size(0, 48), ',
            content
        )
        
        # Only write if changed
        if new_content != content:
            with open(filepath, "w") as f:
                f.write(new_content)
                
print("Patched ElevatedButton styles in admin dashboard")
