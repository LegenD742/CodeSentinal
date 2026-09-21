from app.github_integration.diff_parser import parse_unified_diff

SAMPLE_DIFF = """diff --git a/app.py b/app.py
index e69de29..b6fc4c6 100644
--- a/app.py
+++ b/app.py
@@ -1,3 +1,5 @@
 def greet(name):
-    print("hi")
+    print(f"hi {name}")
+    return None
 
"""


def test_parse_unified_diff_extracts_added_lines():
    files = parse_unified_diff(SAMPLE_DIFF)
    assert len(files) == 1
    file_diff = files[0]
    assert file_diff.new_path == "app.py"
    added = file_diff.added_line_numbers()
    assert added == [2, 3]


def test_parse_unified_diff_handles_no_hunks():
    assert parse_unified_diff("") == []
