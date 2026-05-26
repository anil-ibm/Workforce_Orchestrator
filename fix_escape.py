from pathlib import Path

path = Path("dashboard.html")
text = path.read_text(encoding="utf-8")

old = """    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&")
        .replaceAll("<", "<")
        .replaceAll(">", ">")
        .replaceAll('"', "\"")
        .replaceAll("'", "'");
    }
"""

new = """    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&")
        .replaceAll("<", "<")
        .replaceAll(">", ">")
        .replaceAll('"', """)
        .replaceAll("'", "'");
    }
"""

if old not in text:
    raise SystemExit("target block not found")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("patched dashboard.html escapeHtml")

# Made with Bob
