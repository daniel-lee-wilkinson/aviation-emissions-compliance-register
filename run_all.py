import subprocess

print("🚀 Running data generator (main.py)...")
subprocess.run(["python", "code/main.py"])

print("📦 Importing into database (import_to_sqlite.py)...")
subprocess.run(["python", "code/import_to_sqlite.py"])

print("✅ All steps completed.")
