"""Create matching SVG/PDF diagrams. Requires reportlab and pypdf.

Run from the repository root: python tools/draw_dataset_measurement_paths.py
The PDF is encoded as ASCII with embedded fonts for portable text-file upload.
"""
import html
import io
import math
from pathlib import Path

import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, NameObject, StreamObject

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
W, H = 1440, 810
INK, MUTED = "#172b3a", "#485b68"
BLUE, BLUE_BG = "#12649b", "#edf6fc"
ORANGE, ORANGE_BG = "#a74b12", "#fff5eb"
GREY, GREY_BG = "#a8b7c3", "#f4f7f9"
font_dir = Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("FigureRegular", str(font_dir / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("FigureBold", str(font_dir / "VeraBd.ttf")))
buffer = io.BytesIO()
pdf = canvas.Canvas(buffer, pagesize=(W, H), pageCompression=1, invariant=1,
                    initialFontName="FigureRegular")
pdf.setTitle("EMU and NI DAQ measurement locations and dataset paths")
pdf.setAuthor("")
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
       '<title id="title">EMU and NI DAQ measurement locations and dataset paths</title>',
       '<desc id="desc">A shared AC supply feeds two motor drives at the PCC. An EMU measures aggregated PCC voltage and current; its 16 features feed the classifier evaluated in this paper. A separate NI DAQ acquires motor-terminal phase-current waveforms for the auxiliary raw dataset, which also contains PCC reference channels. The datasets share experiment metadata but have different sample rates and recording coverage.</desc>']


def color(value):
    return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))


def rect(x, y, w, h, fill="white", stroke=GREY, radius=12, width=2):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
    pdf.setFillColorRGB(*color(fill if fill != "white" else "#ffffff"))
    pdf.setStrokeColorRGB(*color(stroke))
    pdf.setLineWidth(width)
    pdf.roundRect(x, H - y - h, w, h, radius, fill=1, stroke=1)


def text(x, y, value, size=22, fill=INK, bold=False, anchor="start"):
    # y is a baseline, shared between the SVG and PDF backends.
    svg.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}" text-anchor="{anchor}">{html.escape(value)}</text>')
    pdf.setFont("FigureBold" if bold else "FigureRegular", size)
    pdf.setFillColorRGB(*color(fill))
    fn = {"start": pdf.drawString, "middle": pdf.drawCentredString, "end": pdf.drawRightString}[anchor]
    fn(x, H - y, value)


def line(points, stroke=INK, width=3, arrow=False):
    joined = " ".join(f"{x},{y}" for x, y in points)
    svg.append(f'<polyline points="{joined}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>')
    pdf.setLineWidth(width)
    pdf.setStrokeColorRGB(*color(stroke))
    path = pdf.beginPath()
    path.moveTo(points[0][0], H - points[0][1])
    for x, y in points[1:]:
        path.lineTo(x, H - y)
    pdf.drawPath(path)
    if arrow:
        x, y = points[-1]
        px, py = points[-2]
        angle = math.atan2(y - py, x - px)
        wings = [(x - 12 * math.cos(angle) + k * 5 * math.sin(angle),
                  y - 12 * math.sin(angle) - k * 5 * math.cos(angle)) for k in (-1, 1)]
        svg.append(f'<polygon points="{x},{y} {wings[0][0]},{wings[0][1]} {wings[1][0]},{wings[1][1]}" fill="{stroke}"/>')
        p = pdf.beginPath()
        p.moveTo(x, H - y)
        for a, b in wings:
            p.lineTo(a, H - b)
        p.close()
        pdf.setFillColorRGB(*color(stroke))
        pdf.drawPath(p, fill=1, stroke=0)


def circle(x, y, r, fill="white", stroke=INK, width=3):
    svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
    pdf.setFillColorRGB(*color(fill if fill != "white" else "#ffffff"))
    pdf.setStrokeColorRGB(*color(stroke))
    pdf.setLineWidth(width)
    pdf.circle(x, H - y, r, fill=1, stroke=1)


rect(0, 0, W, H, stroke="#ffffff", radius=0)
text(28, 44, "Two measurement devices, one motor-drive experiment", 30, bold=True)
text(28, 75, "Measurement location determines what each dataset represents", 21, MUTED)

rect(24, 100, 650, 550, GREY_BG)
text(48, 137, "SHARED PHYSICAL TESTBED", 21, MUTED, True)
rect(50, 310, 130, 70, stroke=INK, radius=7)
text(115, 340, "Three-phase", 18, anchor="middle")
text(115, 365, "AC supply", 20, bold=True, anchor="middle")
line([(180, 345), (330, 345)], arrow=True)
line([(330, 245), (330, 465)])
for cy, motor in [(245, "ACIM"), (465, "PMSM")]:
    line([(330, cy), (370, cy)], arrow=True)
    rect(370, cy - 36, 120, 72, stroke=INK, radius=7)
    text(430, cy + 7, "Drive", 23, bold=True, anchor="middle")
    line([(490, cy), (540, cy)], arrow=True)
    circle(584, cy, 43)
    text(584, cy + 7, motor, 19, bold=True, anchor="middle")
    circle(520, cy, 5, ORANGE, ORANGE, 2)
    text(518, cy - 55, "Terminal tap", 18, ORANGE)

circle(255, 345, 7, BLUE, BLUE, 2)
text(255, 391, "PCC", 25, BLUE, True, "middle")
text(60, 220, "Aggregated", 20, BLUE)
text(60, 247, "voltage/current", 20, BLUE)
line([(255, 345), (255, 164), (740, 164)], BLUE, 4, True)
line([(520, 245), (520, 345), (690, 345), (690, 465), (740, 465)], ORANGE, 4, True)
line([(520, 465), (520, 555), (690, 555), (690, 465)], ORANGE, 4)
text(48, 592, "Both motors operate during each trial.", 21)
text(48, 623, "One motor is attacked at a time.", 21)

rect(740, 100, 675, 225, BLUE_BG, BLUE, width=3)
text(768, 139, "EMU | PCC measurements", 25, BLUE, True)
rect(1190, 112, 199, 33, BLUE, BLUE, radius=5)
text(1289, 135, "USED IN THIS PAPER", 16, "#ffffff", True, "middle")
text(768, 185, "16 voltage/current features | 7 Hz", 23)
text(768, 222, "Window: 128 x 16 | stride: 16 samples", 22)
text(768, 263, "features/", 23, BLUE, True)
line([(900, 255), (946, 255)], BLUE, 3, True)
text(963, 263, "CNN-Bi-GRU classifier", 23, BLUE, True)
text(768, 302, "Paper results use this EMU branch.", 21, MUTED)

rect(740, 365, 675, 285, ORANGE_BG, ORANGE, width=3)
text(768, 406, "NI DAQ | motor-terminal waveforms", 25, ORANGE, True)
text(768, 450, "Released waveform sampling rate: 2 kHz", 22)
text(768, 486, "Window: 2000 x 5 | stride: 1000 samples", 22)
text(768, 524, "raw_waveform_datasets/", 23, ORANGE, True)
text(768, 560, "phase_A/B/C: motor selected per recording", 21)
text(768, 593, "Also archived: PCC_voltage and PCC_current", 21)
text(768, 631, "Auxiliary measurements for dataset users", 21, MUTED)

rect(24, 683, 1391, 105, GREY_BG, GREY)
text(48, 718, "SHARED LABELS", 20, MUTED, True)
text(248, 718, "Normal/attack | motor | phase | severity | speed | load", 23)
text(48, 756, "Use UTC window-end times to compare operating context; sample rates and recording coverage differ.", 21, MUTED)

svg.append("</svg>")
(OUT / "dataset_measurement_paths.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")
pdf.showPage()
pdf.save()

# ASCIIHexDecode preserves stream bytes while making the full PDF ASCII-safe.
# Fonts stay embedded. This also avoids binary transport assumptions in text APIs.
reader = PdfReader(io.BytesIO(buffer.getvalue()))
writer = PdfWriter()
writer.clone_document_from_reader(reader)
for obj in writer._objects:
    if isinstance(obj, StreamObject):
        obj._data = obj._data.hex().encode("ascii") + b">"
        old = obj.get("/Filter")
        filters = [] if old is None else list(old) if isinstance(old, ArrayObject) else [old]
        obj[NameObject("/Filter")] = ArrayObject([NameObject("/ASCIIHexDecode"), *filters])
result = io.BytesIO()
writer.write(result)
data = result.getvalue()
comment = data.splitlines()[1]
if comment.startswith(b"%"):
    replacement = bytes(c if c < 128 else ord("#") for c in comment)
    data = data.replace(comment, replacement, 1)  # Same byte length preserves xref offsets.
data.decode("ascii")
(OUT / "dataset_measurement_paths.pdf").write_bytes(data)
print("Generated matching SVG and PDF diagrams with embedded PDF fonts.")
