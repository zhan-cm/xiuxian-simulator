from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WORD_NS}


@dataclass(frozen=True, slots=True)
class RuleBook:
    source: Path
    text: str
    sha256: str

    REQUIRED_MARKERS = (
        "一、你（AI）的身份",
        "二、输出铁律",
        "六、创角系统",
        "八、境界与突破",
        "十九、存档系统",
        "二十一、AI 行为红线",
    )

    @classmethod
    def load(cls, path: Path) -> "RuleBook":
        source = path.resolve()
        if not source.is_file():
            raise FileNotFoundError(f"找不到原始规则文档：{source}")

        raw = source.read_bytes()
        with zipfile.ZipFile(source) as archive:
            document_xml = archive.read("word/document.xml")

        root = ET.fromstring(document_xml)
        paragraphs: list[str] = []
        for paragraph in root.findall(".//w:p", NS):
            parts: list[str] = []
            for node in paragraph.iter():
                if node.tag == f"{{{WORD_NS}}}t" and node.text:
                    parts.append(node.text)
                elif node.tag == f"{{{WORD_NS}}}tab":
                    parts.append("\t")
                elif node.tag in {f"{{{WORD_NS}}}br", f"{{{WORD_NS}}}cr"}:
                    parts.append("\n")
            line = "".join(parts).strip()
            if line:
                paragraphs.append(line)

        text = "\n".join(paragraphs)
        missing = [marker for marker in cls.REQUIRED_MARKERS if marker not in text]
        if missing:
            raise ValueError("规则文档缺少关键章节：" + "、".join(missing))

        return cls(
            source=source,
            text=text,
            sha256=hashlib.sha256(raw).hexdigest(),
        )

    @property
    def summary(self) -> str:
        return f"已载入 {len(self.text)} 字规则，SHA-256 {self.sha256[:12]}"

