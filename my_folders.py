from pathlib import Path


def print_structure(base_path: Path, indent: int = 0):
    for item in sorted(base_path.iterdir()):
        if item.name.startswith("."):  # Skip hidden files/folders like .git
            continue
        print("  " * indent + f"- {item.name}")
        if item.is_dir():
            print_structure(item, indent + 1)


# Use this at the bottom
print("\n📁 Project File Structure:")
print_structure(Path(__file__).resolve().parent)

from pathlib import Path


def list_files(start_path: Path, prefix=""):
    lines = []
    for path in sorted(start_path.iterdir()):
        if path.name.startswith("."):
            continue
        if path.is_dir():
            lines.append(f"{prefix}📁 {path.name}/")
            lines.extend(list_files(path, prefix + "│   "))
        else:
            lines.append(f"{prefix}├── {path.name}")
    return lines


project_root = (
    Path(__file__).resolve().parent
)  # Adjust if not running from project root
output_md = "\n".join(list_files(project_root))
print("```\n" + output_md + "\n```")
