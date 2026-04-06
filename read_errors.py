import os
for f in ["error.log", "error8.log"]:
    if os.path.exists(f):
        print(f"--- {f} ---")
        try:
            with open(f, "rb") as file:
                content = file.read()
                try:
                    print(content.decode("utf-16"))
                except UnicodeDecodeError:
                    print(content.decode("utf-8", errors="replace"))
        except Exception as e:
            print(f"Failed to read {f}: {e}")
