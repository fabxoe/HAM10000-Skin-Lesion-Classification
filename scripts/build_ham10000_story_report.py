from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "report_assets"
STAMP = datetime.now().strftime("%Y%m%d_%H%M")
OUT_HTML = ROOT / f"HAM10000_ConvNeXt_스토리형보고서_{STAMP}.html"
OUT_PDF = ROOT / f"HAM10000_ConvNeXt_스토리형보고서_{STAMP}.pdf"


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


def metric_cards(cards):
    return "<div class=\"cards\">" + "".join(
        f"""
        <div class="card">
          <div class="card-label">{label}</div>
          <div class="card-value">{value}</div>
          <div class="card-note">{note}</div>
        </div>
        """
        for label, value, note in cards
    ) + "</div>"


def build_html() -> str:
    journey_table = table(
        ["단계", "질문", "실험", "얻은 결론"],
        [
            ["1", "기준 모델은 어디까지 가능한가?", "Backbone / TTA", "ConvNeXt 확률 품질이 분석의 중심이 됨"],
            ["2", "불균형만 해결하면 mel이 좋아질까?", "Focal, WRS, CB Loss", "불균형만으로는 병목을 설명하지 못함"],
            ["3", "mel만 따로 보완하면 어떨까?", "OVR Expert, Cascade", "recall은 올릴 수 있지만 FP 비용이 중요함"],
            ["4", "확률을 믿을 수 있게 만들 수 있나?", "Temperature Scaling", "ECE/NLL 개선으로 신뢰도 보정 가능"],
            ["5", "동일 argmax가 최선인가?", "Class-wise Threshold", "mel/bcc/df 운영점 조정 효과 확인"],
            ["6", "이미지 밖 정보가 도움이 되나?", "Clinical Metadata", "age/sex/localization 결합이 큰 개선 경향"],
            ["7", "효과가 split에 갇힌 것은 아닌가?", "5-Fold OOF", "OOF에서도 calibration/threshold 효과 유지"],
        ],
        "journey-table",
    )

    imbalance_table = table(
        ["실험", "기대한 변화", "실제 결과", "이후 방향"],
        [
            ["Focal Loss + class weight", "소수 클래스 집중 학습", "AUROC 0.9098로 기준보다 하락", "과도한 가중 위험 확인"],
            ["WRS + CE", "소수 클래스 노출 증가", "AUROC 0.9505, mel 개선 제한", "sampling만으로는 부족"],
            ["CB Loss", "가중 과잉 완화", "AUROC 0.9457, mel recall 0.556", "대안이지만 기준 미달"],
        ],
        "wide-table",
    )

    cascade_table = table(
        ["운영점", "mel Recall", "mel Precision", "mel FN", "mel->nv", "nv->mel", "해석"],
        [
            ["Baseline", "0.5157", "0.6928", "108", "87", "35", "기준 오류 양상"],
            ["Aggressive Cascade", "0.7848", "0.4386", "48", "39", "146", "놓치지 않지만 FP가 과도"],
            ["Conservative Cascade", "0.6278", "0.6452", "83", "69", "52", "현실적 screening 운영점"],
        ],
        "wide-table",
    )

    threshold_table = table(
        ["분석", "Before", "After", "의미"],
        [
            ["Temperature Scaling ECE", "0.044550", "0.019226", "확률 신뢰도 개선"],
            ["mel threshold recall", "0.4933", "0.6009", "mel 민감도 보완"],
            ["bcc threshold recall", "0.8155", "0.9029", "기존 bcc 판정이 보수적이었을 가능성"],
            ["df threshold F1", "0.6154", "0.7143", "df는 threshold 조정으로 전반 개선"],
        ],
        "wide-table",
    )

    metadata_table = table(
        ["모델", "Accuracy", "Macro-AUROC", "mel Precision", "mel Recall", "mel F1", "핵심 해석"],
        [
            ["ConvNeXt baseline", "0.8482", "0.9668", "0.7483", "0.4933", "0.5946", "이미지만 사용한 기준점"],
            ["ConvNeXt + metadata", "0.9076", "0.9893", "0.7674", "0.7399", "0.7534", "임상 맥락 결합의 강한 개선 경향"],
            ["Metadata + cost-sensitive", "0.9151", "0.9887", "0.7572", "0.8251", "0.7897", "mel FN 비용을 학습에 반영"],
        ],
        "wide-table",
    )

    oof_table = table(
        ["단계", "Accuracy", "Macro-AUROC", "NLL", "ECE", "mel Recall", "mel FN", "nv->mel"],
        [
            ["OOF raw metadata", "0.8595", "0.9727", "0.3903", "0.0136", "0.5930", "453", "167"],
            ["OOF + Temperature", "0.8595", "0.9727", "0.3894", "0.0102", "0.5930", "453", "167"],
            ["OOF + Temp + mel th 0.30", "0.8546", "0.9727", "0.3894", "0.0102", "0.7125", "320", "323"],
        ],
        "wide-table",
    )

    final_table = table(
        ["결론", "근거", "주의점"],
        [
            ["불균형은 출발점이었지만 최종 답은 아니었다", "Focal/WRS/CB Loss가 기준 모델을 넘지 못함", "소수 클래스 recall 일부 개선은 의미 있음"],
            ["확률과 threshold가 의료적 해석에 중요했다", "Calibration과 class-wise threshold에서 운영점 조정 가능", "FP 비용과 함께 해석 필요"],
            ["metadata는 가장 큰 개선 방향이었다", "single split에서 Acc 0.9076, AUROC 0.9893", "OOF에서는 더 보수적 수치로 재평가 필요"],
            ["OOF 검증은 과장 방지 장치였다", "OOF AUROC 0.9727, ECE 개선 유지", "threshold는 nv->mel FP를 크게 늘림"],
        ],
        "wide-table",
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>HAM10000 ConvNeXt 스토리형 보고서</title>
  <style>
    @page {{
      size: A4;
      margin: 16mm 15mm 17mm;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #f5f7fb;
      color: #172033;
      font-family: "Helvetica Neue", Arial, "Apple SD Gothic Neo", sans-serif;
      font-size: 16px;
      line-height: 1.62;
      letter-spacing: 0;
    }}
    .page {{
      max-width: 900px;
      margin: 20px auto;
      padding: 40px 34px;
      background: #fff;
      border: 1px solid #dde6ef;
      border-radius: 8px;
      box-shadow: 0 4px 10px rgba(18, 30, 50, 0.06);
    }}
    @media print {{
      body {{ background: #fff; }}
      .page {{
        margin: 0;
        padding: 0;
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
      color: #0f2d4a;
      margin: 14px 0 18px;
      font-weight: 800;
    }}
    h2 {{
      font-size: 24px;
      color: #1f77b4;
      margin: 28px 0 10px;
      line-height: 1.3;
    }}
    h3 {{
      font-size: 18px;
      color: #245a80;
      margin: 18px 0 8px;
    }}
    p {{ margin: 8px 0 12px; }}
    .kicker {{
      color: #64748b;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    .hero {{
      border-top: 7px solid #1f77b4;
      position: relative;
    }}
    .lead {{
      font-size: 18px;
      line-height: 1.58;
      color: #24344d;
      margin: 16px 0 20px;
    }}
    .highlight {{
      padding: 16px 18px;
      border-left: 5px solid #2a9d8f;
      background: #edf9f6;
      margin: 16px 0 20px;
      font-weight: 600;
    }}
    .warning {{
      padding: 14px 16px;
      border-left: 5px solid #e76f51;
      background: #fff4ef;
      margin: 15px 0 18px;
    }}
    .chapter {{
      display: inline-block;
      color: #1f77b4;
      background: #e8f3fc;
      border: 1px solid #c7dff0;
      border-radius: 999px;
      padding: 3px 12px;
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin: 16px 0 20px;
    }}
    .card {{
      border: 1px solid #d4e1ec;
      background: #fbfdff;
      padding: 14px 14px;
      border-radius: 8px;
    }}
    .card-label {{
      color: #657184;
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 5px;
    }}
    .card-value {{
      font-size: 26px;
      line-height: 1.15;
      color: #12324f;
      font-weight: 800;
    }}
    .card-note {{
      color: #4b5565;
      font-size: 13px;
      margin-top: 5px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 8px 0 18px;
      font-size: 15.5px;
      line-height: 1.38;
      break-inside: avoid;
    }}
    th, td {{
      border: 1px solid #b7c6d6;
      padding: 8px 9px;
      vertical-align: middle;
      word-break: keep-all;
      overflow-wrap: break-word;
    }}
    th {{
      background: #e8f2fb;
      color: #111827;
      text-align: center;
      font-weight: 800;
    }}
    td {{
      background: #fff;
      text-align: left;
    }}
    td:first-child {{ text-align: center; }}
    .wide-table td:nth-child(n+2) {{ text-align: center; }}
    .journey-table td:nth-child(2),
    .journey-table td:nth-child(3),
    .journey-table td:nth-child(4) {{ text-align: left; }}
    .caption {{
      color: #1f77b4;
      font-size: 16px;
      font-weight: 800;
      margin: 16px 0 6px;
      break-after: avoid;
      page-break-after: avoid;
    }}
    .chart {{
      display: block;
      width: 92%;
      height: auto;
      max-width: 100%;
      margin: 8px auto 18px;
      break-inside: avoid;
      break-before: avoid;
      page-break-before: avoid;
    }}
    .quote {{
      font-size: 20px;
      line-height: 1.5;
      color: #18324d;
      border-left: 5px solid #1f77b4;
      padding: 4px 0 4px 16px;
      margin: 18px 0;
      font-weight: 700;
    }}
    .muted {{ color: #5b6678; }}
    .page-break {{ break-before: page; }}
    .avoid-split {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
  </style>
</head>
<body>
  <section class="page hero">
    <div class="kicker">HAM10000 ConvNeXt Story Report</div>
    <h1>좋은 AUROC를 넘어서,<br>흑색종을 덜 놓치는 모델을 찾는 과정</h1>
    <p class="lead">이 보고서는 HAM10000 7-class 피부 병변 분류에서 ConvNeXt 모델을 개선해 가는 과정을 단순 성능표가 아니라 실험의 줄거리로 정리한 버전이다. 출발점은 클래스 불균형이었지만, 실험이 진행될수록 핵심은 “어떤 확률을 믿고, 어떤 운영점에서 melanoma를 놓치지 않을 것인가”로 이동했다.</p>
    <div class="highlight">최종 메시지: 불균형 대응만으로는 충분하지 않았다. 임상 메타데이터, 확률 보정, threshold, cost-sensitive learning, OOF 검증을 함께 봐야 의료 이미지 분류 보조 모델의 의미가 보인다.</div>
    {metric_cards([
        ("OOF Metadata AUROC", "0.9727", "5-Fold OOF 기준 일반화 추정치"),
        ("OOF ECE", "0.0136 -> 0.0102", "Temperature Scaling 후 신뢰도 개선"),
        ("OOF mel FN", "453 -> 320", "mel threshold 0.30 적용 시"),
    ])}
  </section>

  <section class="page">
    <h2>보고서의 줄거리</h2>
    <p>아래 표는 이 프로젝트의 읽는 순서다. 각 실험은 독립적인 숫자 비교가 아니라, 앞선 실험에서 생긴 의문을 다음 실험이 확인하는 방식으로 이어진다.</p>
    {journey_table}
  </section>

  <section class="page">
    <span class="chapter">Chapter 1</span>
    <h2>처음 질문: 기준 모델은 충분히 강한가?</h2>
    <p>먼저 확인해야 할 것은 모델 구조 자체였다. 의료 이미지 분류에서 성능 개선을 논하려면, 기준 모델이 약해서 생긴 문제인지, 데이터와 의사결정 규칙에서 생긴 문제인지 분리해야 한다.</p>
    <p>Backbone 비교와 입력 해상도, TTA 실험을 통해 ConvNeXt-Tiny를 중심 모델로 정했다. ConvNeXt baseline은 Macro-AUROC 0.966819를 보였고, flip TTA는 AUROC 0.9695까지 안정화했다.</p>
    <div class="caption">그림 1. Backbone/입력 설정별 Macro-AUROC 비교</div>
    <img class="chart" src="{asset('chart_backbone_auroc.png')}">
    <div class="quote">이 시점의 결론은 단순했다. “모델은 충분히 강하다. 이제 오류가 어디서 생기는지 봐야 한다.”</div>
  </section>

  <section class="page">
    <span class="chapter">Chapter 2</span>
    <h2>첫 번째 가설: 클래스 불균형이 전부일까?</h2>
    <p>HAM10000은 nv가 압도적으로 많고 df, vasc 같은 클래스는 적다. 그래서 초기 가설은 자연스럽게 클래스 불균형이었다. Focal Loss, WeightedRandomSampler, Class-Balanced Loss를 적용해 소수 클래스를 더 강하게 보도록 만들었다.</p>
    <div class="caption">표 1. 불균형 대응 실험의 기대와 실제 결과</div>
    {imbalance_table}
    <div class="caption">그림 2. 불균형 대응 실험의 Macro-AUROC 비교</div>
    <img class="chart" src="{asset('chart_imbalance_auroc.png')}">
    <p>결과는 기대와 달랐다. 일부 소수 클래스 recall은 개선되었지만, 대표 성능은 ConvNeXt baseline을 넘지 못했다. 특히 Focal Loss + class weight는 오히려 AUROC를 크게 떨어뜨렸다.</p>
    <div class="warning">해석: melanoma 병목은 단순히 “샘플 수가 적어서”만 생긴 문제가 아니다. mel과 nv의 시각적 유사성, 확률 분포, threshold 선택이 함께 얽혀 있었다.</div>
  </section>

  <section class="page">
    <span class="chapter">Chapter 3</span>
    <h2>두 번째 가설: melanoma만 따로 보완하면 될까?</h2>
    <p>melanoma는 screening 관점에서 놓치면 위험한 클래스다. 그래서 mel vs rest OVR Expert를 따로 만들고, 기존 ConvNeXt 확률과 섞어 보았다.</p>
    <div class="caption">그림 3. OVR blending에 따른 mel precision-recall trade-off</div>
    <img class="chart" src="{asset('chart_ovr_alpha.png')}">
    <p>alpha를 키우면 mel recall은 올라갔다. 그러나 precision은 떨어졌다. 즉, 모델이 melanoma를 더 민감하게 의심하게 만들 수는 있었지만, 그 대가로 false positive가 증가했다.</p>
    <div class="caption">그림 4. OVR alpha 변화에 따른 Macro-AUROC와 mel recall</div>
    <img class="chart" src="{asset('chart_ovr_macro_recall.png')}">
    <p>모든 샘플에 OVR Expert를 섞는 방식은 전체 확률 분포를 흔들었다. 그래서 다음 질문은 더 구체적으로 바뀌었다. “정말 의심스러운 샘플에만 Expert를 적용하면 어떨까?”</p>
  </section>

  <section class="page">
    <span class="chapter">Chapter 4</span>
    <h2>Cascade: 덜 놓치되, 너무 많이 의심하지 않기</h2>
    <p>초기 aggressive Cascade는 mel recall을 크게 올렸지만 nv를 mel로 오분류하는 경우가 크게 증가했다. 따라서 최종적으로는 baseline이 mel 가능성을 0.20 이상으로 보고, OVR Expert도 0.50 이상 확신하는 샘플에만 score boost를 적용하는 Conservative Cascade를 선택했다.</p>
    <div class="caption">표 2. Cascade 운영점 비교</div>
    {cascade_table}
    <div class="caption">그림 5. Conservative Cascade와 Baseline 주요 지표 비교</div>
    <img class="chart" src="{asset('chart_conservative_cascade.png')}">
    <p>Conservative Cascade는 mel FN을 108건에서 83건으로 줄이고, mel->nv 오류를 87건에서 69건으로 줄였다. 동시에 accuracy와 Macro-AUROC는 거의 유지했다. 다만 mel precision은 낮아지고 nv->mel은 증가했으므로, 이 결과는 진단 성능 향상이라기보다 screening 운영점 개선으로 해석해야 한다.</p>
  </section>

  <section class="page">
    <span class="chapter">Chapter 5</span>
    <h2>확률은 맞는데, 믿을 수 있는 확률인가?</h2>
    <p>의료 AI에서는 “맞췄는가”만큼 “얼마나 확신했는가”도 중요하다. Temperature Scaling은 모델의 label 자체를 바꾸지 않고, 확률의 과신 또는 과소신을 조정한다.</p>
    <div class="caption">표 3. Calibration과 threshold의 핵심 변화</div>
    {threshold_table}
    <div class="caption">그림 6. Temperature Scaling 전후 NLL/ECE 변화</div>
    <img class="chart" src="{asset('chart_calibration.png')}">
    <p>Temperature Scaling은 accuracy를 유지하면서 NLL과 ECE를 낮췄다. 이후 threshold 분석에서는 모든 클래스에 같은 argmax 규칙을 쓰는 것이 항상 최선이 아님을 확인했다.</p>
    <div class="caption">그림 7. Threshold 조정 전후 recall/F1 변화</div>
    <img class="chart" src="{asset('chart_threshold.png')}">
  </section>

  <section class="page">
    <span class="chapter">Chapter 6</span>
    <h2>이미지만으로 부족하다면, 임상 맥락을 더한다</h2>
    <p>피부 병변은 이미지 모양만으로 결정되지 않는다. 나이, 성별, 병변 위치는 질환의 사전 확률과 관련될 수 있다. 그래서 ConvNeXt 이미지 feature에 age, sex, localization metadata를 결합했다.</p>
    <div class="caption">표 4. 이미지 모델과 metadata 결합 모델 비교</div>
    {metadata_table}
    <div class="caption">그림 8. Metadata 및 cost-sensitive 실험 주요 지표 비교</div>
    <img class="chart" src="{asset('chart_metadata_multimodal.png')}">
    <p>ConvNeXt + metadata는 단일 validation split에서 큰 개선 경향을 보였다. 여기에 melanoma false negative 비용을 직접 반영한 cost-sensitive learning은 mel recall을 0.8251까지 높였다.</p>
    <div class="warning">주의: 이 결과는 매우 흥미롭지만, 단일 split 결과만으로 “일반화 성능이 확실히 좋아졌다”고 단정하면 안 된다. 그래서 마지막 실험으로 5-Fold OOF 검증을 수행했다.</div>
  </section>

  <section class="page">
    <span class="chapter">Chapter 7</span>
    <h2>마지막 검증: 이 효과가 fold 전체에서도 유지되는가?</h2>
    <p>마지막 실험은 성능을 더 올리기 위한 실험이 아니라 과장을 줄이기 위한 실험이었다. 5-Fold OOF 방식으로 각 fold의 validation 예측을 모아 전체 데이터에 대한 out-of-fold 확률을 만들었다.</p>
    <div class="caption">그림 9. 5-Fold OOF fold별 Accuracy와 Macro-AUROC</div>
    <img class="chart" src="{asset('chart_oof_fold_performance.png')}">
    <div class="caption">표 5. OOF calibration 및 mel threshold 비교</div>
    {oof_table}
    <div class="caption">그림 10. OOF metadata calibration/threshold 주요 지표 비교</div>
    <img class="chart" src="{asset('chart_oof_metadata_validation.png')}">
    <p>OOF raw metadata 모델은 Macro-AUROC 0.9727을 기록했다. 단일 split의 0.9893보다 낮지만, 이는 더 보수적인 일반화 추정치로 보는 것이 맞다. Temperature Scaling은 OOF에서도 ECE를 0.0136에서 0.0102로 낮췄고, mel threshold 0.30은 mel FN을 453건에서 320건으로 줄였다.</p>
    <div class="warning">하지만 threshold는 공짜가 아니었다. nv->mel false positive가 167건에서 323건으로 증가했다. 따라서 이 운영점은 “더 잘 진단한다”가 아니라 “흑색종을 덜 놓치는 screening 설정”으로 표현해야 한다.</div>
  </section>

  <section class="page">
    <span class="chapter">Final</span>
    <h2>최종 결론: 성능표보다 중요한 것은 운영점이다</h2>
    <p>이 프로젝트의 가장 중요한 변화는 실험의 관점이 바뀐 것이다. 처음에는 클래스 불균형을 고치면 문제가 해결될 것이라고 생각했지만, 실제로는 확률 보정, threshold, metadata, 비용 민감 학습, OOF 검증이 함께 필요했다.</p>
    <div class="caption">표 6. 최종 해석 요약</div>
    {final_table}
    <div class="quote">최종적으로 이 모델은 “진단 모델”이라기보다, 흑색종 누락을 줄이기 위한 분류 보조 및 screening 운영점 탐색으로 해석하는 것이 가장 안전하다.</div>
    <p>향후 연구에서는 cost-sensitive metadata 모델과 Cascade 운영점을 5-Fold 체계 안에서 함께 검증하고, threshold 적용으로 늘어난 false positive가 실제 임상 workflow에서 감당 가능한 수준인지 평가해야 한다. Grad-CAM이나 XAI 분석을 추가한다면, 모델이 실제 병변 영역에 더 반응하는지 보조적으로 확인할 수 있지만, 이를 진단 근거로 과장해서는 안 된다.</p>
  </section>
</body>
</html>"""


if __name__ == "__main__":
    OUT_HTML.write_text(build_html(), encoding="utf-8")
    print(OUT_HTML)
    print(OUT_PDF)
