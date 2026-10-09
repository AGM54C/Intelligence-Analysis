"""Export the human-maintained dataset cards as an Excel-friendly UTF-8 CSV."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = []
    for path in sorted(ROOT.glob("[0-9][0-9]-*/*.md")):
        text = path.read_text(encoding="utf-8")
        fields = dict(re.findall(r"^\| (类型|模态与标签|获取状态) \| (.*?) \|$", text, re.M))
        links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", text)
        rows.append({
            "编号": path.name.split("-", 1)[0],
            "名称": text.splitlines()[0].removeprefix("# "),
            "分类": path.parent.name,
            **fields,
            "说明文件": path.relative_to(ROOT).as_posix(),
            "外部入口与下载链接": " ; ".join(f"{label}: {url}" for label, url in links),
            "数据获取方式": "原始数据通过官方入口获取",
            "信息日期": "2026-10-09",
        })
    if not rows:
        raise SystemExit("No dataset cards found")
    output = ROOT / "数据集清单.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} resource cards to {output}")


if __name__ == "__main__":
    main()
