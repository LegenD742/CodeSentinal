import Editor from "@monaco-editor/react";

/**
 * Read-only Monaco viewer for a file's content, with a marker gutter
 * for lines that have findings attached.
 */
export default function DiffViewer({ filePath, content, findingLines = [] }) {
  const language = filePath?.endsWith(".py")
    ? "python"
    : filePath?.match(/\.(ts|tsx)$/)
    ? "typescript"
    : filePath?.match(/\.(js|jsx)$/)
    ? "javascript"
    : "plaintext";

  return (
    <div className="rounded-lg border border-line overflow-hidden">
      <div className="flex items-center justify-between bg-surface border-b border-line px-3 py-2">
        <span className="text-xs font-mono text-ink/60">{filePath}</span>
        {findingLines.length > 0 && (
          <span className="text-xs text-ink/40">{findingLines.length} finding(s) flagged</span>
        )}
      </div>
      <Editor
        height="420px"
        language={language}
        value={content || "// No content available for this file"}
        theme="vs"
        options={{
          readOnly: true,
          minimap: { enabled: false },
          fontSize: 13,
          fontFamily: "'JetBrains Mono', monospace",
          scrollBeyondLastLine: false,
          lineNumbers: "on",
          glyphMargin: true,
        }}
      />
    </div>
  );
}
