from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
CHART_DIR = ROOT / "report_assets"
STAMP = datetime.now().strftime("%Y%m%d_%H%M")
OUT_PDF = ROOT / f"HAM10000_ConvNeXt_보고서_PDF직접생성_{STAMP}.pdf"

FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
FONT_NAME = "ArialUnicode"

BLUE = colors.HexColor("#1F77B4")
NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#2A9D8F")
LIGHT_BLUE = colors.HexColor("#EAF4FF")
SOFT_BLUE = colors.HexColor("#F5F9FF")
GRID = colors.HexColor("#9AA7B4")
TEXT = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#5B6370")


def register_fonts() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(FONT_PATH)
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName=FONT_NAME,
            fontSize=24,
            leading=31,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=12,
            wordWrap="CJK",
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=17,
            textColor=MUTED,
            alignment=TA_LEFT,
            spaceAfter=12,
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName=FONT_NAME,
            fontSize=17,
            leading=23,
            textColor=BLUE,
            spaceBefore=12,
            spaceAfter=8,
            wordWrap="CJK",
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName=FONT_NAME,
            fontSize=12.5,
            leading=18,
            textColor=NAVY,
            spaceBefore=9,
            spaceAfter=5,
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=17,
            textColor=TEXT,
            spaceAfter=7,
            wordWrap="CJK",
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=16,
            textColor=TEXT,
            wordWrap="CJK",
        ),
        "table_head": ParagraphStyle(
            "table_head",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.black,
            wordWrap="CJK",
        ),
        "table_center": ParagraphStyle(
            "table_center",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.black,
            wordWrap="CJK",
        ),
        "table_left": ParagraphStyle(
            "table_left",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            alignment=TA_LEFT,
            textColor=colors.black,
            wordWrap="CJK",
        ),
        "table_head_tiny": ParagraphStyle(
            "table_head_tiny",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.black,
            wordWrap="CJK",
        ),
        "table_center_tiny": ParagraphStyle(
            "table_center_tiny",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.black,
            wordWrap="CJK",
        ),
        "table_left_tiny": ParagraphStyle(
            "table_left_tiny",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            alignment=TA_LEFT,
            textColor=colors.black,
            wordWrap="CJK",
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["BodyText"],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            textColor=BLUE,
            spaceBefore=7,
            spaceAfter=4,
            wordWrap="CJK",
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("\n", "<br/>"), style)


def is_text_col(header: str) -> bool:
    return any(key in header for key in ["실험", "목적", "결과", "해석", "근거", "이유", "판단", "범주"])


def make_table(title: str, headers: list[str], rows: list[list[str]], widths: list[float], st: dict, compact=False):
    tiny = compact == "tiny"
    head_style = st["table_head_tiny"] if tiny else st["table_head"]
    center_style = st["table_center_tiny"] if tiny else st["table_center"]
    left_style = st["table_left_tiny"] if tiny else st["table_left"]
    data = [[p(h, head_style) for h in headers]]
    for row in rows:
        out = []
        for i, val in enumerate(row):
            style = left_style if is_text_col(headers[i]) else center_style
            out.append(p(str(val), style))
        data.append(out)
    tbl = Table(data, colWidths=[w * cm for w in widths], repeatRows=1, hAlign="CENTER")
    pad_y = 3 if tiny else (4 if compact else 6)
    tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.45, GRID),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), pad_y),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad_y),
            ]
        )
    )
    return [p(title, st["caption"]), tbl, Spacer(1, 0.22 * cm)]


def callout(text: str, st: dict):
    tbl = Table([[p(text, st["small"])]], colWidths=[24.0 * cm], hAlign="CENTER")
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.0, SOFT_BLUE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return [tbl, Spacer(1, 0.25 * cm)]


def chart(path: str, caption: str, st: dict):
    img_path = CHART_DIR / path
    if not img_path.exists():
        return []
    img = Image(str(img_path), width=18.5 * cm, height=8.8 * cm)
    img.hAlign = "CENTER"
    return [KeepTogether([p(caption, st["caption"]), img]), Spacer(1, 0.18 * cm)]


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_NAME, 12)
    canvas.setFillColor(MUTED)
    page_w, page_h = landscape(A4)
    canvas.drawRightString(page_w - 1.6 * cm, page_h - 1.0 * cm, "HAM10000 ConvNeXt 보고서")
    canvas.drawCentredString(page_w / 2, 0.9 * cm, "보고서")
    canvas.restoreState()


def build() -> Path:
    register_fonts()
    st = styles()
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=landscape(A4),
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.4 * cm,
        title="HAM10000 ConvNeXt 보고서",
        author="Codex",
    )
    story = []

    story += [
        p("HAM10000 피부 병변 분류를 위한 ConvNeXt 기반 분류기 성능 개선 연구", st["title"]),
        Spacer(1, 0.35 * cm),
    ]
    story += callout(
        "핵심 메시지: 단순한 손실 함수 변경이나 샘플링보다 ConvNeXt 기반 확률 품질, Temperature Scaling, 클래스별 threshold 분석이 의료영상 분류 보조 모델의 실제 활용성을 더 직접적으로 높였다.",
        st,
    )

    story += [p("1. 요약", st["h1"])]
    story += [
        p("본 프로젝트는 HAM10000 피부 병변 7-class 분류 문제에서 ConvNeXt-Tiny 기반 모델을 중심으로 성능 개선 가능성을 검토하였다. 초기 가설은 클래스 불균형이 핵심 병목이라는 것이었으나, Focal Loss, WeightedRandomSampler, Class-Balanced Loss 실험 결과 불균형 대응만으로는 Macro-AUROC 기준 대표 성능을 충분히 개선하지 못했다.", st["body"]),
        p("이후 분석의 초점은 확률 품질과 decision rule로 이동하였다. Temperature Scaling은 accuracy를 유지하면서 NLL과 ECE를 낮췄고, Class-wise Threshold Optimization은 mel, bcc, df에서 recall 또는 F1 개선을 확인했다. 특히 threshold 실험은 모든 클래스에 동일한 argmax 규칙을 적용하는 것이 항상 최적은 아님을 보여준다.", st["body"]),
    ]

    story += [p("2. 실험 흐름과 채택 판단", st["h1"])]
    story += make_table(
        "표 1. 실험별 목적 및 채택 여부",
        ["실험", "목적", "핵심 결과", "채택 판단"],
        [
            ["Baseline", "기준 성능과 오류 양상 확인", "ConvNeXt baseline Macro-AUROC 0.966819", "기준 모델"],
            ["Backbone 비교", "구조 차이에 따른 feature 품질 비교", "ConvNeXt-Tiny가 비교 backbone 중 우수", "채택"],
            ["224->384", "병변 경계와 세부 패턴 보존", "ResNet 기준 AUROC 0.8995->0.9065", "부분 채택"],
            ["Flip TTA", "추론 안정화", "AUROC 0.9695", "채택"],
            ["Focal Loss", "소수 클래스 강조", "AUROC 하락 및 accuracy 저하", "미채택"],
            ["WeightedRandomSampler", "소수 클래스 노출 증가", "df/akiec recall 개선, mel 제한", "보조 실험"],
            ["Class-Balanced Loss", "가중 과잉 완화", "Focal보다 안정적, 기준 모델 미달", "대안 실험"],
            ["OVR Expert", "mel 보완", "mel AUROC/recall 일부 개선", "보완용"],
            ["Ensemble", "확률 결합 성능 확인", "Soft Voting/Ridge 차이 작음", "미채택"],
            ["Temperature Scaling", "확률 신뢰도 보정", "NLL/ECE 개선", "채택"],
            ["Threshold Optimization", "클래스별 sensitivity/F1 개선", "mel/bcc/df 개선 확인", "중요 분석"],
        ],
        [5.5, 6.2, 7.4, 4.5],
        st,
        compact=True,
    )

    story += [p("3. 데이터와 평가 기준", st["h1"])]
    story += [
        p("HAM10000은 nv, mel, bkl, bcc, akiec, vasc, df 등 7개 피부 병변 클래스로 구성된다. 클래스 분포가 균등하지 않기 때문에 accuracy만으로는 소수 클래스 성능을 충분히 설명하기 어렵다.", st["body"]),
        p("본 보고서는 Macro-AUROC를 중심 지표로 사용했다. Macro-AUROC는 각 클래스를 동일한 비중으로 평가하므로 다수 클래스에 의해 성능이 가려지는 문제를 줄일 수 있다. 다만 threshold 조정은 AUROC 자체를 직접 개선하는 기법이 아니라, 확률을 class label로 바꾸는 decision rule을 조정하는 분석이다.", st["body"]),
    ]

    story += [p("4. Backbone, 해상도, TTA", st["h1"])]
    story += make_table(
        "표 2. Backbone 비교",
        ["모델", "Accuracy", "Macro-AUROC", "해석"],
        [
            ["ResNet18", "확인됨", "비교 기준", "기본 CNN backbone으로 기준선 제공"],
            ["EfficientNet-B0", "확인됨", "비교 대상", "효율적인 구조이나 최종 선택은 아님"],
            ["ConvNeXt-Tiny", "0.8482", "0.966819", "분석의 중심 backbone"],
        ],
        [5.5, 3.5, 4.0, 10.5],
        st,
    )
    story += chart("chart_backbone_auroc.png", "그림 1. Backbone/입력 설정별 Macro-AUROC 비교", st)
    story += make_table(
        "표 3. 입력 해상도 및 TTA 비교",
        ["설정", "Accuracy", "Macro-AUROC", "해석"],
        [
            ["ResNet 224", "확인됨", "0.8995", "기준 해상도"],
            ["ResNet 384", "확인됨", "0.9065", "세부 패턴 보존으로 개선 경향"],
            ["ConvNeXt baseline", "0.8482", "0.966819", "주요 분석 기준 확률"],
            ["ConvNeXt + flip TTA", "0.8522", "0.9695", "추론 안정화로 개선"],
        ],
        [6.2, 3.5, 4.0, 9.8],
        st,
    )
    story += [
        p("입력 해상도 증가는 의료영상에서 병변 경계와 색/texture 패턴을 더 보존한다는 점에서 의미가 있다. TTA는 재학습 없이 flip 기반 예측 평균을 사용해 확률 변동을 줄였고, 최종 ConvNeXt 실험에서 성능 안정화 효과를 보였다.", st["body"]),
    ]

    story += [p("5. 클래스 불균형 대응 실험", st["h1"])]
    story += make_table(
        "표 4. 불균형 대응 실험 비교",
        ["실험", "핵심 수치", "결과 해석", "판단"],
        [
            ["Focal Loss + class weight", "AUROC 0.9098 / TTA 0.9111", "소수 클래스 가중이 과도하게 작동했을 가능성", "미채택"],
            ["WeightedRandomSampler + CE", "AUROC 0.9505", "일부 소수 클래스 recall 개선, mel 개선 제한", "보조 실험"],
            ["Class-Balanced Loss", "AUROC 0.9457 / mel recall 0.556", "Focal보다 안정적이나 기준 모델에는 미달", "대안 실험"],
        ],
        [6.0, 4.8, 9.0, 3.0],
        st,
    )
    story += chart("chart_imbalance_auroc.png", "그림 2. 불균형 대응 실험의 Macro-AUROC 비교", st)
    story += [
        p("불균형 대응 실험은 초기 가설을 검증하는 핵심 단계였다. 결과적으로 소수 클래스 recall은 일부 개선되었지만 Macro-AUROC 기준 대표 성능을 대체하지 못했다. 따라서 melanoma 성능 병목은 단순한 클래스 빈도 문제가 아니라 시각적 유사성, 확률 분포, threshold 설정과 결합된 문제로 해석하는 것이 타당하다.", st["body"]),
    ]

    story += [p("6. Expert Model과 Ensemble", st["h1"])]
    story += [
        p("OVR Expert는 melanoma vs rest 이진 전문가 모델로 설계되었다. 이 실험은 기준 모델을 대체하기보다 melanoma 민감도 보완 가능성을 확인하는 목적에 가깝다.", st["body"]),
    ]
    story += chart("chart_ovr_alpha.png", "그림 3. mel precision-recall trade-off by OVR blending", st)
    story += [
        p("OVR Soft Ensemble의 alpha 값 변화에 따른 정밀도-재현율(Precision-Recall) 변화는 임상적 의사결정 관점에서 매우 중요한 트레이드오프를 보여준다. alpha가 커질수록(즉, OVR Expert의 비중이 늘어날수록) 흑색종(mel)의 재현율(Recall)은 0.49에서 최대 0.67까지 크게 향상되지만, 정밀도(Precision)는 0.75에서 0.56으로 감소한다. 두 지표는 alpha ≈ 0.70 부근에서 약 61%로 교차하며 뒤집히는 양상을 보인다. 흑색종은 조기 진단을 놓쳤을 때의 치명도가 매우 높은 질환이므로, F1-score가 극대화되는 alpha 0.50~0.65 구간뿐만 아니라, 오진 위험(False Positive)을 다소 감수하더라도 실제 환자를 놓치지 않는(Recall 우위) alpha 0.70 이상 영역의 운영 지점을 선택하는 전략적 의사결정이 필요하다.", st["body"]),
    ]
    story += make_table(
        "표 5. Ensemble 비교",
        ["실험", "Accuracy", "Macro-AUROC", "해석"],
        [
            ["Soft Voting", "확인됨", "0.9472", "단순 확률 평균 기준"],
            ["Logistic Stacking", "0.8114", "0.9431", "accuracy는 높였지만 AUROC는 낮음"],
            ["Ridge Stacking alpha=10", "확인됨", "0.9449", "Stacking 계열 중 가장 우수"],
            ["Weighted Ensemble", "확인됨", "0.9452", "기대만큼 개선되지 않음"],
            ["OVR Soft alpha=0.05", "baseline 유지", "0.966891", "미세 개선, alpha 증가 시 AUROC 감소"],
        ],
        [6.2, 3.5, 4.0, 10.0],
        st,
    )

    story += [PageBreak(), p("7. 확률 보정과 Threshold 분석", st["h1"])]
    story += [
        p("Temperature Scaling은 logits를 하나의 temperature로 나누어 softmax 확률의 sharpness를 조정하는 후처리다. label을 바꾸는 기법이 아니라 확률 신뢰도를 개선하는 calibration 기법이다.", st["body"]),
    ]
    story += make_table(
        "표 6. Temperature Scaling 전후 비교",
        ["설정", "Temperature", "Accuracy", "Macro-AUROC", "NLL", "ECE"],
        [
            ["Before", "1.000000", "0.848228", "0.966819", "0.464353", "0.044550"],
            ["After", "1.354742", "0.848228", "0.966914", "0.439376", "0.019226"],
        ],
        [3.2, 4.0, 4.0, 4.4, 3.2, 3.2],
        st,
    )
    story += chart("chart_calibration.png", "그림 4. Temperature Scaling 전후 NLL/ECE 변화", st)
    story += [PageBreak()]
    story += make_table(
        "표 7. Threshold Optimization 전후 비교",
        ["Class", "Th.", "Accuracy", "Precision", "Recall", "F1", "해석"],
        [
            ["mel", "0.28", "0.8482\n-> 0.8447", "0.7483\n-> 0.6505", "0.4933\n-> 0.6009", "0.5946\n-> 0.6247", "recall 크게 증가\naccuracy 소폭 감소"],
            ["bcc", "0.37", "0.8482\n-> 0.8497", "0.6885\n-> 0.6739", "0.8155\n-> 0.9029", "0.7467\n-> 0.7718", "recall/F1/accuracy 개선"],
            ["df", "0.18", "0.8482\n-> 0.8497", "0.7500\n-> 0.7895", "0.5217\n-> 0.6522", "0.6154\n-> 0.7143", "모든 지표 개선"],
        ],
        [1.6, 1.6, 3.4, 3.4, 3.4, 3.2, 7.2],
        st,
        compact="tiny",
    )
    story += make_table(
        "표 8. Threshold Optimization 변화량 요약",
        ["Class", "Threshold", "Accuracy 변화", "Recall 변화", "Precision 변화", "F1 변화", "핵심 해석"],
        [
            ["mel", "0.28", "-0.0035", "+0.1076", "-0.0978", "+0.0301", "FP 허용, sensitivity 개선"],
            ["bcc", "0.37", "+0.0015", "+0.0874", "-0.0146", "+0.0251", "recall/F1/accuracy 동시 개선"],
            ["df", "0.18", "+0.0015", "+0.1304", "+0.0395", "+0.0989", "모든 지표 개선"],
        ],
        [1.8, 2.4, 3.0, 3.0, 3.2, 2.8, 7.5],
        st,
        compact=True,
    )
    story += chart("chart_threshold.png", "그림 5. Threshold 조정 전후 recall/F1 변화", st)
    story += [
        p("mel은 threshold 0.28에서 recall이 0.4933에서 0.6009로 증가했고, accuracy 감소는 0.0035 수준으로 제한적이었다. precision 감소는 FP 증가 가능성을 의미하지만, melanoma FN을 줄이는 screening 관점에서는 의미 있는 운영점이다.", st["body"]),
        p("bcc는 threshold 0.37에서 recall과 F1뿐 아니라 accuracy도 소폭 개선되었다. 이는 기존 ConvNeXt의 bcc 판단이 다소 보수적이었고, threshold 조정만으로 놓치던 bcc 샘플을 일부 회수할 수 있음을 시사한다.", st["body"]),
        p("df는 precision, recall, F1, accuracy가 동시에 개선되었다. 일반적으로 precision과 recall은 trade-off 관계지만, df에서는 threshold가 지나치게 높게 설정되어 있었을 가능성이 크다.", st["body"]),
    ]
    story += callout(
        "Threshold 분석의 결론은 모든 클래스에 동일한 argmax decision rule을 적용하는 것이 항상 최적은 아니라는 점이다. 클래스별 확률 분포와 오류 비용을 고려한 threshold 설정은 실제 배포 환경에서 sensitivity와 F1을 조정하는 효과적인 방법이 될 수 있다.",
        st,
    )

    story += [PageBreak(), p("8. 종합 비교와 해석", st["h1"])]
    story += make_table(
        "표 9. 전체 실험 요약표",
        ["범주", "대표 실험", "핵심 수치", "채택/미채택 근거"],
        [
            ["기준 모델", "ConvNeXt baseline", "Acc 0.8482 / AUROC 0.966819", "분석의 중심 모델"],
            ["추론 개선", "Flip TTA", "Acc 0.8522 / AUROC 0.9695", "안정적 개선으로 채택"],
            ["해상도", "224->384", "AUROC 0.8995->0.9065", "세부 패턴 보존 가능성"],
            ["불균형", "Focal Loss", "AUROC 0.9098", "과도한 가중으로 미채택"],
            ["불균형", "WeightedRandomSampler", "AUROC 0.9505", "mel 개선 제한"],
            ["불균형", "Class-Balanced Loss", "AUROC 0.9457", "대안 실험으로 해석"],
            ["Expert", "OVR Soft alpha=0.05", "AUROC 0.966891", "개선 폭 매우 작음"],
            ["Ensemble", "Soft Voting/Ridge", "0.9472 / 0.9449", "기준 baseline 미달"],
            ["Calibration", "Temperature Scaling", "ECE 0.044550->0.019226", "확률 신뢰도 개선"],
            ["Threshold", "mel/bcc/df", "recall 및 F1 개선", "운영점 분석으로 중요"],
        ],
        [4.4, 6.0, 6.0, 8.0],
        st,
        compact=True,
    )
    story += make_table(
        "표 10. 보고서 가치가 높은 실험 순위",
        ["순위", "실험", "보고서에서 중요한 이유"],
        [
            ["1", "Class-wise Threshold Optimization", "mel/bcc/df 비교로 동일 argmax 규칙의 한계 확인"],
            ["2", "OVR Expert mel vs rest", "melanoma 보완 가능성을 별도 전문가 모델로 검증"],
            ["3", "Ridge Stacking", "Stacking 계열 중 가장 안정적이나 Soft Voting과 차이는 작음"],
            ["4", "Resolution 224->384", "세부 texture와 병변 경계 보존 효과 확인"],
            ["5", "TTA", "재학습 없이 추론 안정성을 높임"],
            ["6", "WeightedRandomSampler", "일부 recall 개선, mel 병목 개선은 제한적"],
            ["7", "Class-Balanced Loss", "Focal보다 안정적이나 기준 모델에는 미달"],
            ["8", "Soft Voting", "단순 확률 평균의 기준점과 한계 확인"],
            ["9", "Logistic Stacking", "accuracy는 높였지만 Macro-AUROC는 낮아짐"],
            ["10", "Focal Loss", "과도한 소수 클래스 가중의 위험 확인"],
        ],
        [2.2, 7.0, 15.0],
        st,
        compact=True,
    )
    story += [
        p("전체 실험을 종합하면 초기의 클래스 불균형 가설은 일부만 설명력이 있었다. 불균형 대응은 소수 클래스 recall 개선에는 도움이 되었지만, Macro-AUROC 기준 대표 성능을 대체하지 못했다. 반면 확률 보정과 threshold 분석은 모델 구조를 바꾸지 않고도 의료영상 분류에서 중요한 신뢰도와 sensitivity trade-off를 직접 다룰 수 있었다.", st["body"]),
    ]

    story += [p("9. 결론 및 향후 연구", st["h1"])]
    story += [
        p("본 연구에서는 HAM10000 피부 병변 분류 문제에 대해 ConvNeXt-Tiny 기반 모델을 중심으로 다양한 성능 개선 실험을 수행하였다. 실험 결과, 단순한 손실 함수 변경이나 샘플링 전략보다 입력 해상도, TTA, 확률 보정, 클래스별 threshold 분석이 더 실질적인 효과를 보였다.", st["body"]),
        p("특히 Temperature Scaling은 모델의 예측 확률 신뢰도를 개선했으며, Class-wise Threshold Optimization은 melanoma, bcc, df에서 sensitivity 및 F1 개선을 보였다. 따라서 ConvNeXt-Tiny 기반 모델을 중심으로 하되, 확률 보정과 클래스별 threshold 분석을 결합하는 방향이 가장 타당한 결론이다.", st["body"]),
        p("한계도 명확하다. 본 연구는 단일 validation split에 기반하므로 외부 검증 데이터셋에서 동일한 threshold와 calibration 효과가 유지되는지 확인해야 한다. 향후에는 ConvNeXt V2, Vision Transformer, 임상 메타데이터 결합, cost-sensitive learning, 다단계 Expert 모델, calibration 기법 비교를 수행할 수 있다.", st["body"]),
    ]

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return OUT_PDF


if __name__ == "__main__":
    print(build())
