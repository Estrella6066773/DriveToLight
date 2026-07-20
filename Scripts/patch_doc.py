#!/usr/bin/env python3
"""
UTF-8 安全的 Markdown 文档补丁脚本。

用于通过临时文件传入 old/new 文本，避免 Shell 编码中转导致中文乱码。
所有读写统一使用 UTF-8 无 BOM。

用法：
    # 单段替换（old / new 各写临时 UTF-8 文本文件）
    python Scripts/patch_doc.py --file "Docs/程序设计/示例.md" \
        --old-file patch/old.txt --new-file patch/new.txt

    # 多段替换（replacements.json 为 [{"old":"...","new":"..."}, ...]）
    python Scripts/patch_doc.py --file "Docs/..." \
        --replacements patch/replacements.json

    # 仅预览
    python Scripts/patch_doc.py --file "Docs/..." \
        --old-file patch/old.txt --new-file patch/new.txt --dry-run

规则：
    - old 文本须在目标文件中存在且唯一（出现恰好一次）；
    - 多段模式下，所有 old 均须唯一；按数组顺序依次应用替换。

参见 Docs 规则 docs-utf8-editing.mdc。
"""

import argparse
import json
import sys
from pathlib import Path


def read_utf8(path: str) -> str:
    """读取 UTF-8 文本文件（无 BOM 输出）。"""
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_utf8(path: str, content: str) -> None:
    """写入 UTF-8 无 BOM 文本文件。"""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def patch_single(file_path: str, old_text: str, new_text: str, dry_run: bool = False) -> bool:
    """对目标文件执行单段替换。返回 True 表示成功。"""
    content = read_utf8(file_path)

    count = content.count(old_text)
    if count == 0:
        print(f"[ERROR] old 文本在目标文件中不存在。", file=sys.stderr)
        print(f"  文件: {file_path}", file=sys.stderr)
        print(f"  old 开头: {old_text[:80]}...", file=sys.stderr)
        return False

    if count > 1:
        print(f"[ERROR] old 文本在目标文件中出现了 {count} 次（要求唯一）。", file=sys.stderr)
        print(f"  文件: {file_path}", file=sys.stderr)
        return False

    new_content = content.replace(old_text, new_text, 1)

    if new_content == content:
        print("[WARN] 替换后内容无变化，old 与 new 可能相同。", file=sys.stderr)
        return True

    if dry_run:
        print(f"[DRY RUN] 将在 {file_path} 中替换 1 处。")
        return True

    write_utf8(file_path, new_content)
    print(f"[OK] 已替换 {file_path} 中的 1 处匹配。")
    return True


def patch_multi(file_path: str, replacements: list[dict], dry_run: bool = False) -> bool:
    """对目标文件按顺序执行多段替换。"""
    content = read_utf8(file_path)

    for i, entry in enumerate(replacements):
        old_text = entry.get("old", "")
        new_text = entry.get("new", "")

        count = content.count(old_text)
        if count == 0:
            print(f"[ERROR] 第 {i + 1} 段 old 文本在文件中不存在。", file=sys.stderr)
            print(f"  old 开头: {old_text[:80]}...", file=sys.stderr)
            return False

        if count > 1:
            print(f"[ERROR] 第 {i + 1} 段 old 文本出现了 {count} 次（要求唯一）。", file=sys.stderr)
            return False

        content = content.replace(old_text, new_text, 1)

    if dry_run:
        print(f"[DRY RUN] 将在 {file_path} 中按顺序替换 {len(replacements)} 段。")
        return True

    write_utf8(file_path, content)
    print(f"[OK] 已在 {file_path} 中按顺序替换 {len(replacements)} 段。")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UTF-8 安全的 Markdown 文档补丁脚本"
    )
    parser.add_argument("--file", required=True, help="目标 Markdown 文件路径")
    parser.add_argument("--old-file", help="包含 old 文本的 UTF-8 临时文件")
    parser.add_argument("--new-file", help="包含 new 文本的 UTF-8 临时文件")
    parser.add_argument(
        "--replacements",
        help="多段替换 JSON 文件（格式: [{\"old\":\"...\",\"new\":\"...\"}, ...]）",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写入")

    args = parser.parse_args()

    has_single = bool(args.old_file or args.new_file)
    has_multi = bool(args.replacements)

    if has_single and has_multi:
        print("[ERROR] --old-file/--new-file 与 --replacements 不能同时使用。", file=sys.stderr)
        sys.exit(1)

    if has_single:
        if not args.old_file or not args.new_file:
            print("[ERROR] --old-file 和 --new-file 必须同时提供。", file=sys.stderr)
            sys.exit(1)
        success = patch_single(args.file, read_utf8(args.old_file), read_utf8(args.new_file), args.dry_run)
    elif has_multi:
        with open(args.replacements, "r", encoding="utf-8") as f:
            replacements = json.load(f)
        if not isinstance(replacements, list):
            print("[ERROR] --replacements JSON 须为数组。", file=sys.stderr)
            sys.exit(1)
        success = patch_multi(args.file, replacements, args.dry_run)
    else:
        print("[ERROR] 须提供 --old-file --new-file 或 --replacements。", file=sys.stderr)
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
