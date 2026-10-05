from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "report_assets"
STAMP = datetime.now().strftime("%Y%m%d_%H%M")
OUT_HTML = ROOT / f"HAM10000_ConvNeXt_보고서_HTML_{STAMP}.html"
OUT_PDF = ROOT / f"HAM10000_ConvNeXt_보고서_HTML_{STAMP}.pdf"


def asset(name: str) -> str:
    path = ASSETS / name
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def table(headers, rows, cls=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "\n".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"""
    <table class="{cls}">
      <thead><tr>{head}</tr></thead>
      <tbody>{body}</tbody>
    </table>
    """


def build_html() -> str:
    exp_table = table(
        ["실험", "목적", "핵심 결과", "채택 판단"],
        [
            ["Baseline", "기준 성능과 오류 양상 확인", "ConvNeXt baseline Macro-AUROC 0.966819", "기준 모델"],
            ["Backbone 비교", "구조 차이에 따른 feature 품질 비교", "ConvNeXt-Tiny가 비교 backbone 중 우수", "채택"],
            ["224->384", "병변 경계와 세부 패턴 보존", "ResNet 기준 AUROC 0.8995->0.9065", "부분 채택"],
            ["Flip TTA", "추론 안정화", "AUROC 0.9695", "채택"],
            ["Focal Loss", "소수 클래스 강조", "AUROC 하락 및 accuracy 저하", "미채택"],
            ["WRS", "소수 클래스 노출 증가", "df/akiec recall 개선, mel 제한", "보조 실험"],
            ["CB Loss", "가중 과잉 완화", "Focal보다 안정적, 기준 모델 미달", "대안 실험"],
            ["OVR Expert", "mel 보완", "mel AUROC/recall 일부 개선", "보완용"],
            ["Conservative Cascade", "mel 의심 샘플에 선택적 Expert 보정", "mel recall 0.5157->0.6278 / FN 108->83", "운영점 후보"],
            ["Ensemble", "확률 결합 성능 확인", "Soft Voting/Ridge 차이 작음", "미채택"],
            ["Temperature Scaling", "확률 신뢰도 보정", "NLL/ECE 개선", "채택"],
            ["Threshold Optimization", "클래스별 sensitivity/F1 개선", "mel/bcc/df 개선 확인", "중요 분석"],
            ["Clinical Metadata", "age/sex/localization 결합", "Acc 0.9076 / AUROC 0.9893", "추가 검증 필요"],
        ],
        "decision-table",
    )

    backbone_table = table(
        ["모델", "Accuracy", "Macro-AUROC", "해석"],
        [
            ["ResNet18", "확인됨", "비교 기준", "기본 CNN backbone으로 기준선 제공"],
            ["EffNet-B0", "확인됨", "비교 대상", "효율적인 구조이나 최종 선택은 아님"],
            ["ConvNeXt-Tiny", "0.8482", "0.966819", "분석의 중심 backbone"],
        ],
    )

    resolution_table = table(
        ["설정", "Accuracy", "Macro-AUROC", "해석"],
        [
            ["ResNet 224", "확인됨", "0.8995", "기준 해상도"],
            ["ResNet 384", "확인됨", "0.9065", "세부 패턴 보존으로 개선 경향"],
            ["ConvNeXt baseline", "0.8482", "0.966819", "주요 분석 기준 확률"],
            ["ConvNeXt + flip TTA", "0.8522", "0.9695", "추론 안정화로 개선"],
        ],
    )

    imbalance_table = table(
        ["실험", "핵심 수치", "결과 해석", "판단"],
        [
            ["Focal Loss + class weight", "AUROC 0.9098<br>TTA 0.9111", "소수 클래스 가중이 과도하게 작동했을 가능성", "미채택"],
            ["WRS + CE", "AUROC 0.9505", "일부 소수 클래스 recall 개선, mel 개선 제한", "보조 실험"],
            ["CB Loss", "AUROC 0.9457<br>mel recall 0.556", "Focal보다 안정적이나 기준 모델에는 미달", "대안 실험"],
        ],
    )

    ensemble_table = table(
        ["실험", "Accuracy", "Macro-AUROC", "해석"],
        [
            ["Soft Voting", "확인됨", "0.9472", "단순 확률 평균 기준"],
            ["Logistic Stacking", "0.8114", "0.9431", "accuracy는 높였지만 AUROC는 낮음"],
            ["Ridge Stacking alpha=10", "확인됨", "0.9449", "Stacking 계열 중 가장 우수"],
            ["Weighted Ensemble", "확인됨", "0.9452", "기대만큼 개선되지 않음"],
            ["OVR Soft alpha=0.05", "baseline 유지", "0.966891", "미세 개선, alpha 증가 시 AUROC 감소"],
            ["Conservative Cascade", "0.8497", "0.9701", "mel FN 감소, FP 증가는 제한적"],
        ],
    )

    cascade_table = table(
        ["모델", "Accuracy", "Macro-AUROC", "mel Precision", "mel Recall", "mel F1", "mel FN", "mel->nv", "nv->mel"],
        [
            ["Baseline", "0.8477", "0.9699", "0.6928", "0.5157", "0.5913", "108", "87", "35"],
            ["Aggressive Cascade", "0.8048", "0.9688", "0.4386", "0.7848", "0.5627", "48", "39", "146"],
            ["Conservative Cascade", "0.8497", "0.9701", "0.6452", "0.6278", "0.6364", "83", "69", "52"],
        ],
        "wide-table",
    )

    temp_table = table(
        ["설정", "Temperature", "Accuracy", "Macro-AUROC", "NLL", "ECE"],
        [
            ["Before", "1.000000", "0.848228", "0.966819", "0.464353", "0.044550"],
            ["After", "1.354742", "0.848228", "0.966914", "0.439376", "0.019226"],
        ],
        "metric-table",
    )

    threshold_table = table(
        ["Class", "Threshold", "Accuracy", "Precision", "Recall", "F1", "해석"],
        [
            ["mel", "0.28", "0.8482 -> 0.8447", "0.7483 -> 0.6505", "0.4933 -> 0.6009", "0.5946 -> 0.6247", "recall 크게 증가<br>accuracy 소폭 감소"],
            ["bcc", "0.37", "0.8482 -> 0.8497", "0.6885 -> 0.6739", "0.8155 -> 0.9029", "0.7467 -> 0.7718", "recall/F1/accuracy 개선"],
            ["df", "0.18", "0.8482 -> 0.8497", "0.7500 -> 0.7895", "0.5217 -> 0.6522", "0.6154 -> 0.7143", "모든 지표 개선"],
        ],
        "wide-table",
    )

    threshold_delta_table = table(
        ["Class", "Threshold", "Accuracy 변화", "Recall 변화", "Precision 변화", "F1 변화", "핵심 해석"],
        [
            ["mel", "0.28", "-0.0035", "+0.1076", "-0.0978", "+0.0301", "FP 허용, sensitivity 개선"],
            ["bcc", "0.37", "+0.0015", "+0.0874", "-0.0146", "+0.0251", "recall/F1/accuracy 동시 개선"],
            ["df", "0.18", "+0.0015", "+0.1304", "+0.0395", "+0.0989", "모든 지표 개선"],
        ],
        "wide-table",
    )

    metadata_table = table(
        ["실험", "Accuracy", "Macro-AUROC", "mel Precision", "mel Recall", "mel F1", "해석"],
        [
            ["ConvNeXt baseline", "0.8482", "0.966819", "0.7483", "0.4933", "0.5946", "이미지 기반 기준 모델"],
            ["ConvNeXt + metadata", "0.9076", "0.989303", "0.7674", "0.7399", "0.7534", "임상 정보 결합 후 개선 경향"],
            ["Metadata + cost-sensitive", "0.9151", "0.988742", "0.7572", "0.8251", "0.7897", "mel recall/F1 중심 개선"],
        ],
        "wide-table",
    )

    cost_sensitive_table = table(
        ["모델", "Accuracy", "Macro-AUROC", "mel Precision", "mel Recall", "mel F1", "mel FN", "mel->nv"],
        [
            ["ConvNeXt + metadata", "0.9076", "0.989303", "0.7674", "0.7399", "0.7534", "-", "-"],
            ["Metadata + cost-sensitive", "0.9151", "0.988742", "0.7572", "0.8251", "0.7897", "39", "26"],
        ],
        "wide-table",
    )

    cost_auc_table = table(
        ["Class", "AUROC"],
        [
            ["akiec", "0.995054"],
            ["bcc", "0.995294"],
            ["bkl", "0.980207"],
            ["df", "0.997211"],
            ["mel", "0.970157"],
            ["nv", "0.983829"],
            ["vasc", "0.999439"],
        ],
        "metric-table",
    )

    oof_fold_table = table(
        ["Fold", "Best Epoch", "Valid Loss", "Accuracy", "Macro-AUROC"],
        [
            ["1", "3", "0.3510", "0.8742", "0.9796"],
            ["2", "3", "0.3984", "0.8557", "0.9704"],
            ["3", "3", "0.3963", "0.8602", "0.9749"],
            ["4", "3", "0.3999", "0.8527", "0.9754"],
            ["5", "3", "0.4061", "0.8547", "0.9765"],
        ],
        "metric-table",
    )

    oof_comparison_table = table(
        ["단계", "Accuracy", "Macro-AUROC", "NLL", "ECE", "mel Precision", "mel Recall", "mel F1", "mel FN", "mel->nv", "nv->mel"],
        [
            ["OOF raw metadata", "0.8595", "0.9727", "0.3903", "0.0136", "0.6762", "0.5930", "0.6319", "453", "347", "167"],
            ["Temperature Scaling", "0.8595", "0.9727", "0.3894", "0.0102", "0.6762", "0.5930", "0.6319", "453", "347", "167"],
            ["Temp + mel threshold 0.30", "0.8546", "0.9727", "0.3894", "0.0102", "0.5994", "0.7125", "0.6511", "320", "241", "323"],
        ],
        "wide-table",
    )

    oof_threshold_table = table(
        ["Threshold", "Accuracy", "mel Precision", "mel Recall", "mel F1", "mel FN", "mel->nv", "nv->mel", "해석"],
        [
            ["0.30", "0.8546", "0.5994", "0.7125", "0.6511", "320", "241", "323", "selection score 기준 최상"],
            ["0.32", "0.8557", "0.6126", "0.6918", "0.6498", "343", "261", "292", "precision과 FP가 조금 더 안정적"],
            ["0.28", "0.8517", "0.5809", "0.7287", "0.6465", "302", "228", "356", "recall/FN 개선은 크지만 FP 증가"],
        ],
        "wide-table",
    )

    metadata_auc_table = table(
        ["Class", "AUROC"],
        [
            ["akiec", "0.995324"],
            ["bcc", "0.995192"],
            ["bkl", "0.982930"],
            ["df", "0.999561"],
            ["mel", "0.968491"],
            ["nv", "0.984181"],
            ["vasc", "0.999439"],
        ],
        "metric-table",
    )

    summary_table = table(
        ["범주", "대표 실험", "핵심 수치", "채택/미채택 근거"],
        [
            ["기준 모델", "ConvNeXt baseline", "Acc 0.8482 / AUROC 0.966819", "분석의 중심 모델"],
            ["추론 개선", "Flip TTA", "Acc 0.8522 / AUROC 0.9695", "안정적 개선으로 채택"],
            ["해상도", "224->384", "AUROC 0.8995->0.9065", "세부 패턴 보존 가능성"],
            ["불균형", "Focal Loss", "AUROC 0.9098", "과도한 가중으로 미채택"],
            ["불균형", "WRS", "AUROC 0.9505", "mel 개선 제한"],
            ["불균형", "CB Loss", "AUROC 0.9457", "대안 실험으로 해석"],
            ["Expert", "OVR Soft alpha=0.05", "AUROC 0.966891", "개선 폭 매우 작음"],
            ["Ensemble", "Soft Voting/Ridge", "0.9472 / 0.9449", "기준 baseline 미달"],
            ["Calibration", "Temperature Scaling", "ECE 0.044550->0.019226", "확률 신뢰도 개선"],
            ["Threshold", "mel/bcc/df", "recall 및 F1 개선", "운영점 분석으로 중요"],
            ["Multimodal", "ConvNeXt + metadata", "Acc 0.9076 / AUROC 0.9893", "개선 경향, 단일 split 한계"],
            ["Cost-sensitive", "Metadata + cost-sensitive", "mel recall 0.8251 / F1 0.7897", "mel FN 감소 목적에 부합"],
            ["Cascade", "Conservative Cascade", "mel FN 108->83 / mel F1 0.5913->0.6364", "선택적 Expert 보정으로 운영점 개선"],
            ["OOF 검증", "5-Fold metadata calibration/threshold", "OOF AUROC 0.9727 / ECE 0.0136->0.0102", "단일 split 과적합 여부 점검"],
        ],
    )

    rank_table = table(
        ["순위", "실험", "보고서에서 중요한 이유"],
        [
            ["1", "Class-wise Threshold Optimization", "mel/bcc/df 비교로 동일 argmax 규칙의 한계 확인"],
            ["2", "Clinical Metadata 결합", "age/sex/localization이 이미지 feature를 보완할 가능성 확인"],
            ["3", "Cost-Sensitive Learning", "mel false negative 비용을 학습 단계에 반영"],
            ["4", "OVR Expert mel vs rest", "melanoma 보완 가능성을 별도 전문가 모델로 검증"],
            ["5", "Conservative Cascade", "Expert를 모든 샘플이 아니라 mel 의심 샘플에 선택적으로 적용"],
            ["6", "5-Fold OOF 검증", "metadata + calibration/threshold 효과가 fold 전체에서도 유지되는지 확인"],
            ["7", "Ridge Stacking", "Stacking 계열 중 가장 안정적이나 Soft Voting과 차이는 작음"],
            ["8", "Resolution 224->384", "세부 texture와 병변 경계 보존 효과 확인"],
            ["9", "TTA", "재학습 없이 추론 안정성을 높임"],
            ["10", "WRS", "일부 recall 개선, mel 병목 개선은 제한적"],
            ["11", "CB Loss", "Focal보다 안정적이나 기준 모델에는 미달"],
            ["12", "Focal Loss", "과도한 소수 클래스 가중의 위험 확인"],
        ],
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>HAM10000 ConvNeXt 보고서</title>
  <style>
    @page {{
      size: A4;
      margin: 18mm 16mm 18mm;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: #18212f;
      background: #f8fafc;
      font-family: "Helvetica Neue", Arial, "Apple SD Gothic Neo", sans-serif;
      font-size: 16px;
      line-height: 1.58;
      letter-spacing: 0;
      font-weight: 400;
    }}
    .page {{
      break-after: auto;
      min-height: 0;
      position: relative;
      padding: 40px 32px;
      max-width: 900px;
      margin: 20px auto;
      background: white;
      border: 1px solid #e2e8f0;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
      border-radius: 8px;
    }}
    .page:last-child {{ break-after: auto; }}
    @media print {{
      body {{
        background: white;
      }}
      .page {{
        padding: 0;
        margin: 0;
        max-width: none;
        border: none;
        box-shadow: none;
        border-radius: 0;
      }}
    }}
    h1, h2, h3, p {{ margin: 0; }}
    h1 {{
      font-size: 34px;
      line-height: 1.18;
      color: #14324f;
      font-weight: 700;
      margin: 18px 0 24px;
      letter-spacing: 0;
    }}
    h2 {{
      font-size: 24px;
      line-height: 1.3;
      color: #1f77b4;
      font-weight: 700;
      margin: 24px 0 10px;
    }}
    h3 {{
      font-size: 18px;
      line-height: 1.35;
      color: #275b82;
      margin: 22px 0 8px;
      font-weight: 700;
    }}
    p {{ margin: 7px 0 11px; }}
    .hero {{
      padding-top: 10px;
      border-top: 6px solid #1f77b4;
    }}
    .kicker {{
      color: #657184;
      font-size: 16px;
      margin-bottom: 10px;
      font-weight: 600;
    }}
    .callout {{
      margin: 16px 0 20px;
      padding: 16px 18px;
      background: #eef7ff;
      border-left: 5px solid #2a9d8f;
      color: #162335;
      font-size: 16px;
      line-height: 1.55;
    }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      align-items: start;
    }}
    .caption {{
      color: #1f77b4;
      font-size: 16px;
      font-weight: 700;
      margin: 14px 0 6px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: auto;
      margin: 0 0 16px;
      font-size: 16px;
      line-height: 1.38;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    tr {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    th, td {{
      border: 1px solid #b6c4d1;
      padding: 9px 10px;
      vertical-align: middle;
      overflow-wrap: break-word;
      word-break: keep-all;
      hyphens: none;
    }}
    th {{
      background: #e8f2fb;
      color: #111827;
      font-weight: 700;
      text-align: center;
    }}
    td {{
      background: #ffffff;
      text-align: left;
    }}
    td:nth-child(1),
    .metric-table td,
    .wide-table td:nth-child(-n+6) {{
      text-align: center;
    }}
    .wide-table {{
      font-size: 15.5px;
    }}
    .wide-table th, .wide-table td {{
      padding: 8px 8px;
    }}
    .decision-table th:nth-child(1), .decision-table td:nth-child(1) {{ width: 22%; }}
    .decision-table th:nth-child(2), .decision-table td:nth-child(2) {{ width: 29%; }}
    .decision-table th:nth-child(3), .decision-table td:nth-child(3) {{ width: 33%; }}
    .decision-table th:nth-child(4), .decision-table td:nth-child(4) {{ width: 16%; }}
    .chart {{
      display: block;
      width: 92%;
      height: auto;
      max-width: 100%;
      object-fit: contain;
      margin: 6px auto 18px;
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .caption {{
      break-after: avoid;
    }}
    .avoid-split {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    .section-note {{
      padding: 12px 14px;
      background: #f6f8fb;
      border: 1px solid #e0e7ef;
      margin: 14px 0 18px;
    }}
    section.page + section.page {{
      padding-top: 0;
    }}
    .muted {{ color: #596579; }}
    .avoid-break {{ page-break-inside: avoid; }}
    .new-page {{ break-before: page; }}
  </style>
</head>
<body>
  <section class="page hero">
    <div class="kicker">HAM10000 ConvNeXt 보고서</div>
    <h1>HAM10000 피부 병변 분류를 위한<br>ConvNeXt 기반 분류기 성능 개선 연구</h1>
    <div class="callout">
      핵심 메시지: 단순한 손실 함수 변경이나 샘플링보다 ConvNeXt 기반 확률 품질, Temperature Scaling, 클래스별 threshold 분석이 의료영상 분류 보조 모델의 실제 활용성을 더 직접적으로 높였다.
    </div>
    <h2>1. 요약</h2>
    <p>본 프로젝트는 HAM10000 피부 병변 7-class 분류 문제에서 ConvNeXt-Tiny 기반 모델을 중심으로 성능 개선 가능성을 검토하였다. 초기 가설은 클래스 불균형이 핵심 병목이라는 것이었으나, Focal Loss, WeightedRandomSampler, Class-Balanced Loss 실험 결과 불균형 대응만으로는 Macro-AUROC 기준 대표 성능을 충분히 개선하지 못했다.</p>
    <p>이후 분석의 초점은 확률 품질과 decision rule로 이동하였다. Temperature Scaling은 accuracy를 유지하면서 NLL과 ECE를 낮췄고, Class-wise Threshold Optimization은 mel, bcc, df에서 recall 또는 F1 개선을 확인했다. 특히 threshold 실험은 모든 클래스에 동일한 argmax 규칙을 적용하는 것이 항상 최적은 아님을 보여준다.</p>
    <h2>2. 실험 흐름과 채택 판단</h2>
    <div class="caption">표 1. 실험별 목적 및 채택 여부</div>
    {exp_table}
  </section>

  <section class="page">
    <h2>3. 데이터와 평가 기준</h2>
    <p>HAM10000은 nv, mel, bkl, bcc, akiec, vasc, df 등 7개 피부 병변 클래스로 구성된다. 클래스 분포가 균등하지 않기 때문에 accuracy만으로는 소수 클래스 성능을 충분히 설명하기 어렵다.</p>
    <p>본 보고서는 Macro-AUROC를 중심 지표로 사용했다. Macro-AUROC는 각 클래스를 동일한 비중으로 평가하므로 다수 클래스에 의해 성능이 가려지는 문제를 줄일 수 있다. 다만 threshold 조정은 AUROC 자체를 직접 개선하는 기법이 아니라, 확률을 class label로 바꾸는 decision rule을 조정하는 분석이다.</p>
    <h2>4. Backbone, 해상도, TTA</h2>
    <div class="caption">표 2. Backbone 비교</div>
    {backbone_table}
    <div class="caption">표 3. 입력 해상도 및 TTA 비교</div>
    {resolution_table}
    <div class="caption">그림 1. Backbone/입력 설정별 Macro-AUROC 비교</div>
    <img class="chart" src="{asset('chart_backbone_auroc.png')}">
    <p>입력 해상도 증가는 의료영상에서 병변 경계와 색/texture 패턴을 더 보존한다는 점에서 의미가 있다. TTA는 재학습 없이 flip 기반 예측 평균을 사용해 확률 변동을 줄였고, 최종 ConvNeXt 실험에서 성능 안정화 효과를 보였다.</p>
  </section>

  <section class="page">
    <h2>5. 클래스 불균형 대응 실험</h2>
    <div class="caption">표 4. 불균형 대응 실험 비교</div>
    {imbalance_table}
    <div class="caption">그림 2. 불균형 대응 실험의 Macro-AUROC 비교</div>
    <img class="chart" src="{asset('chart_imbalance_auroc.png')}">
    <p>불균형 대응 실험은 초기 가설을 검증하는 핵심 단계였다. 결과적으로 소수 클래스 recall은 일부 개선되었지만 Macro-AUROC 기준 대표 성능을 대체하지 못했다. 따라서 melanoma 성능 병목은 단순한 클래스 빈도 문제가 아니라 시각적 유사성, 확률 분포, threshold 설정과 결합된 문제로 해석하는 것이 타당하다.</p>
    <h2>6. Expert Model과 Ensemble</h2>
    <p>OVR Expert는 melanoma vs rest 이진 전문가 모델로 설계되었다. 이 실험은 기준 모델을 대체하기보다 melanoma 민감도 보완 가능성을 확인하는 목적에 가깝다.</p>
    <div class="caption">그림 3. mel precision-recall trade-off by OVR blending</div>
    <img class="chart" src="{asset('chart_ovr_alpha.png')}">
    <p>OVR Soft Ensemble의 alpha 값 변화에 따른 정밀도-재현율(Precision-Recall) 변화는 melanoma 보완 실험의 성격을 보여준다. alpha가 커질수록, 즉 OVR Expert의 비중이 늘어날수록 흑색종(mel)의 재현율(Recall)은 0.49에서 최대 0.677까지 증가했지만, 정밀도(Precision)는 0.75에서 0.56으로 감소했다. 이는 모델이 melanoma를 더 민감하게 잡도록 바뀌는 대신 False Positive가 늘어날 수 있음을 의미한다. 따라서 OVR Soft Ensemble은 최종 성능을 일괄적으로 높인 방법이라기보다, melanoma 민감도 보완 가능성을 확인한 보조 실험으로 해석하는 것이 적절하다.</p>
    <div class="caption">그림 4. OVR alpha 변화에 따른 Macro-AUROC와 mel recall 보조 비교</div>
    <img class="chart" src="{asset('chart_ovr_macro_recall.png')}">
    <p>보조 비교에서는 OVR Expert 비중이 커질수록 melanoma recall은 증가하지만, 전체 클래스를 평균한 Macro-AUROC는 소폭 낮아지는 경향을 확인할 수 있다. 이 결과는 7장의 threshold 분석과 구분해서 해석해야 한다. 6장은 ConvNeXt 확률과 OVR Expert 확률을 섞었을 때의 효과를 보는 실험이고, 7장은 이미 얻은 확률의 신뢰도와 판정 기준을 조정하는 분석이다.</p>
    <h3>6.1 Cascade Expert 운영점 보수화</h3>
    <p>Soft Ensemble은 모든 샘플에 OVR Expert 확률을 섞기 때문에 alpha가 커질수록 전체 확률 분포가 함께 흔들리는 문제가 있었다. 이를 보완하기 위해 baseline 모델이 melanoma 가능성을 일정 수준 이상으로 본 샘플에만 Expert 보정을 적용하는 Cascade 구조를 추가로 검토했다.</p>
    <div class="caption">표 5. Cascade Expert 운영점 비교</div>
    {cascade_table}
    <div class="caption">그림 5. Conservative Cascade와 Baseline 주요 지표 비교</div>
    <img class="chart" src="{asset('chart_conservative_cascade.png')}">
    <p>초기 aggressive Cascade는 mel recall을 0.5157에서 0.7848로 크게 높이고 mel FN을 108건에서 48건으로 줄였지만, mel precision이 0.4386까지 낮아지고 nv를 mel로 오분류한 사례가 35건에서 146건으로 증가했다. 따라서 최종 운영점으로는 과도하게 민감한 설정이었다.</p>
    <p>보수화한 Conservative Cascade는 baseline mel 확률 0.20 이상, OVR Expert mel 확률 0.50 이상인 샘플에만 score boost를 적용했다. 그 결과 accuracy와 Macro-AUROC는 baseline과 거의 같거나 소폭 개선되었고, melanoma recall은 0.5157에서 0.6278로 증가했다. mel FN은 108건에서 83건으로 줄었으며, mel을 nv로 놓친 오류도 87건에서 69건으로 감소했다. 다만 mel precision은 0.6928에서 0.6452로 낮아지고 nv->mel 오분류가 35건에서 52건으로 증가했으므로, 이 방법은 최종 진단 성능 향상이라기보다 흑색종 누락을 줄이기 위한 screening 운영점으로 해석하는 것이 적절하다.</p>
  </section>

  <section class="page">
    <div class="caption">표 6. Ensemble 비교</div>
    {ensemble_table}
    <h2 class="new-page">7. 확률 보정과 Threshold 분석</h2>
    <p>Temperature Scaling은 logits를 하나의 temperature로 나누어 softmax 확률의 sharpness를 조정하는 후처리다. label을 바꾸는 기법이 아니라 확률 신뢰도를 개선하는 calibration 기법이다.</p>
    <div class="caption">표 7. Temperature Scaling 전후 비교</div>
    {temp_table}
    <div class="caption">그림 6. Temperature Scaling 전후 NLL/ECE 변화</div>
    <img class="chart" src="{asset('chart_calibration.png')}">
  </section>

  <section class="page">
    <div class="caption">표 8. Threshold Optimization 전후 비교</div>
    {threshold_table}
    <div class="caption">표 9. Threshold Optimization 변화량 요약</div>
    {threshold_delta_table}
    <div class="caption">그림 7. Threshold 조정 전후 recall/F1 변화</div>
    <img class="chart" src="{asset('chart_threshold.png')}">
  </section>

  <section class="page">
    <p>mel은 threshold 0.28에서 recall이 0.4933에서 0.6009로 증가했고, accuracy 감소는 0.0035 수준으로 제한적이었다. precision 감소는 FP 증가 가능성을 의미하지만, melanoma FN을 줄이는 screening 관점에서는 의미 있는 운영점이다.</p>
    <p>bcc는 threshold 0.37에서 recall과 F1뿐 아니라 accuracy도 소폭 개선되었다. 이는 기존 ConvNeXt의 bcc 판단이 다소 보수적이었고, threshold 조정만으로 놓치던 bcc 샘플을 일부 회수할 수 있음을 시사한다.</p>
    <p>df는 precision, recall, F1, accuracy가 동시에 개선되었다. 일반적으로 precision과 recall은 trade-off 관계지만, df에서는 threshold가 지나치게 높게 설정되어 있었을 가능성이 크다.</p>
    <div class="callout">Threshold 분석의 결론은 모든 클래스에 동일한 argmax decision rule을 적용하는 것이 항상 최적은 아니라는 점이다. 클래스별 확률 분포와 오류 비용을 고려한 threshold 설정은 실제 배포 환경에서 sensitivity와 F1을 조정하는 효과적인 방법이 될 수 있다.</div>
    <h2>8. 임상 메타데이터 결합 추가 실험</h2>
    <p>추가 실험으로 age, sex, localization 정보를 ConvNeXt 이미지 feature와 결합한 멀티모달 모델을 학습했다. ConvNeXt의 마지막 classifier를 제거해 이미지 feature를 추출하고, 메타데이터는 age 표준화와 sex/localization one-hot encoding 후 MLP를 통과시켜 이미지 feature와 concatenate하였다.</p>
    <div class="caption">표 10. ConvNeXt baseline과 임상 메타데이터 결합 모델 비교</div>
    {metadata_table}
    <div class="caption">그림 8. 임상 메타데이터 및 cost-sensitive 실험 주요 지표 비교</div>
    <img class="chart" src="{asset('chart_metadata_multimodal.png')}">
  </section>

  <section class="page">
    <div class="caption">표 11. 임상 메타데이터 결합 모델의 class-wise AUROC</div>
    {metadata_auc_table}
    <p>메타데이터 결합 모델은 validation set에서 Macro-AUROC 0.9893, accuracy 0.9076을 기록했고, melanoma recall도 0.7399로 개선 경향을 보였다. 이는 나이, 성별, 병변 위치 같은 임상적 맥락이 이미지 feature만으로 구분하기 어려운 mel과 nv 판단에 보조 정보를 제공했을 가능성을 시사한다.</p>
    <p>다만 이 결과는 단일 validation split에서 얻은 추가 실험 결과이므로, 기존 baseline과 완전히 동일한 학습 조건 및 fold에서 반복 검증하기 전까지는 일반화 성능 향상으로 단정하기 어렵다. 특히 metadata는 데이터 수집 환경의 편향을 포함할 수 있으므로, 의료 AI 관점에서는 성능 수치와 함께 편향 가능성을 같이 검토해야 한다.</p>
    <h2>9. Cost-Sensitive Learning 추가 실험</h2>
    <p>Cost-Sensitive Learning은 메타데이터 결합 모델에 melanoma false negative 비용을 직접 반영한 실험이다. 손실 함수에서 실제 mel 샘플이 다른 클래스로 갈 확률에 비용을 부여했고, 특히 mel을 nv로 분류하는 오류에 더 큰 비용을 설정했다.</p>
    <div class="caption">표 12. 임상 메타데이터 모델과 cost-sensitive 모델 비교</div>
    {cost_sensitive_table}
    <div class="caption">표 13. Cost-sensitive 모델의 class-wise AUROC</div>
    {cost_auc_table}
  </section>

  <section class="page">
    <p>Cost-sensitive 모델은 validation set에서 accuracy 0.9151, Macro-AUROC 0.9887을 기록했다. 특히 melanoma recall은 0.7399에서 0.8251로 증가했고, melanoma F1도 0.7534에서 0.7897로 개선되었다. 이는 threshold를 사후 조정하는 것과 달리, 학습 단계에서 melanoma false negative 비용을 반영한 전략이 melanoma 민감도 향상에 기여했을 가능성을 보여준다.</p>
    <p>다만 Macro-AUROC는 0.9893에서 0.9887로 소폭 낮아졌으므로, 전체 ranking 성능이 명확히 개선되었다고 보기보다는 melanoma recall을 우선한 screening 목적의 개선으로 해석하는 것이 적절하다. 또한 nv를 mel로 예측한 false positive도 존재하므로, recall 향상과 precision/FP 변화는 함께 검토해야 한다.</p>
    <h2>10. 5-Fold OOF 일반화 검증</h2>
    <p>마지막 실험은 단일 validation split에서 관찰된 metadata 결합, calibration, melanoma threshold 효과가 fold 전체에서도 유지되는지 확인하기 위해 수행했다. 5-Fold Stratified OOF 방식으로 각 fold의 validation 예측을 모아 전체 10,015개 샘플에 대한 OOF 확률을 구성했다.</p>
    <div class="caption">표 14. 5-Fold OOF fold별 성능</div>
    {oof_fold_table}
    <div class="caption">그림 9. 5-Fold OOF fold별 Accuracy와 Macro-AUROC</div>
    <img class="chart" src="{asset('chart_oof_fold_performance.png')}">
    <div class="caption">표 15. OOF Calibration 및 mel threshold 비교</div>
    {oof_comparison_table}
  </section>

  <section class="page">
    <div class="caption">표 16. OOF mel threshold 주요 후보</div>
    {oof_threshold_table}
    <div class="caption">그림 10. OOF metadata calibration/threshold 주요 지표 비교</div>
    <img class="chart" src="{asset('chart_oof_metadata_validation.png')}">
    <p>OOF raw metadata 모델은 Accuracy 0.8595, Macro-AUROC 0.9727을 기록했다. 이는 단일 split의 metadata 실험보다 낮지만, 5개 fold 전체에서 얻은 OOF 결과라는 점에서 더 보수적인 일반화 추정치로 볼 수 있다. fold별 Macro-AUROC는 0.9704~0.9796 범위로 나타나 fold 간 편차는 존재하지만, 전체적으로 높은 ranking 성능은 유지되었다.</p>
    <p>Temperature Scaling은 accuracy와 class label을 바꾸지 않으면서 NLL을 0.3903에서 0.3894로, ECE를 0.0136에서 0.0102로 낮췄다. 개선 폭은 크지 않지만, OOF 기준에서도 calibration 효과가 유지되었다는 점에서 의미가 있다.</p>
    <p>mel threshold 0.30을 적용하면 melanoma recall은 0.5930에서 0.7125로 증가했고, melanoma FN은 453건에서 320건으로 감소했다. 동시에 mel->nv 오류도 347건에서 241건으로 줄었다. 반면 mel precision은 0.6762에서 0.5994로 낮아지고, nv->mel 오류는 167건에서 323건으로 증가했다. 따라서 threshold 효과는 fold 전체에서도 유지되지만, screening 민감도를 높이는 대신 false positive 비용이 커지는 trade-off로 해석해야 한다.</p>
    <h2>11. 종합 비교와 해석</h2>
    <div class="caption">표 17. 전체 실험 요약표</div>
    {summary_table}
  </section>

  <section class="page">
    <div class="caption">표 18. 보고서 가치가 높은 실험 순위</div>
    {rank_table}
    <p>전체 실험을 종합하면 초기의 클래스 불균형 가설은 일부만 설명력이 있었다. 불균형 대응은 소수 클래스 recall 개선에는 도움이 되었지만, Macro-AUROC 기준 대표 성능을 대체하지 못했다. 반면 확률 보정과 threshold 분석은 모델 구조를 크게 바꾸지 않고도 의료영상 분류에서 중요한 신뢰도와 sensitivity trade-off를 직접 다룰 수 있었다.</p>
    <h2>12. 결론 및 향후 연구</h2>
    <p>본 연구에서는 HAM10000 피부 병변 분류 문제에 대해 ConvNeXt-Tiny 기반 모델을 중심으로 다양한 성능 개선 실험을 수행하였다. 단순한 손실 함수 변경이나 샘플링 전략보다 입력 해상도, TTA, 확률 보정, 클래스별 threshold 분석이 더 실질적인 효과를 보였다.</p>
    <p>추가로 수행한 임상 메타데이터 결합 실험은 Macro-AUROC 0.9893과 melanoma recall 0.7399를 기록했고, cost-sensitive learning은 melanoma recall을 0.8251까지 높였다. Conservative Cascade는 OVR Expert를 모든 샘플에 적용하지 않고 melanoma 의심 샘플에만 선택적으로 적용했을 때, mel FN을 108건에서 83건으로 줄이면서 accuracy와 Macro-AUROC를 거의 유지할 수 있음을 보였다. 마지막 5-Fold OOF 검증에서는 metadata 모델이 OOF Macro-AUROC 0.9727을 기록했고, Temperature Scaling이 ECE를 0.0136에서 0.0102로 낮췄으며, mel threshold 0.30이 melanoma FN을 453건에서 320건으로 줄였다. 다만 threshold 적용은 nv->mel false positive를 167건에서 323건으로 증가시켰으므로, 최종 운영점은 의료 screening 목적과 추가 검사 비용을 함께 고려해 선택해야 한다.</p>
  </section>
</body>
</html>"""


if __name__ == "__main__":
    OUT_HTML.write_text(build_html(), encoding="utf-8")
    print(OUT_HTML)
    print(OUT_PDF)
