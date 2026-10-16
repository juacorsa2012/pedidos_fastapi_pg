import os

with open("project_dump.txt", "w", encoding="utf-8") as out:
    for root, dirs, files in os.walk("app"):
        # Excluir carpetas innecesarias
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".venv", "node_modules"]]
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                out.write(f"\n{'='*60}\n📄 {path}\n{'='*60}\n")
                with open(path, "r", encoding="utf-8") as code:
                    out.write(code.read())
print("✅ Listo! Archivo generado: project_dump.txt")