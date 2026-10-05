# HAM10000 Skin Lesion Classification

PyTorch / ConvNeXt 기반 **HAM10000 7-class 피부병변 분류 프로젝트**입니다.

전체 성능뿐 아니라 **class-level failure, melanoma false negative, calibration, decision threshold, generalization**을 분리해서 검증하는 데 초점을 두었습니다.

> This project is for research and portfolio purposes only. It is not intended for medical diagnosis.

## 1. Problem

HAM10000은 `nv` 비중이 큰 불균형 데이터셋입니다. 높은 Accuracy나 Macro-AUROC만 확인할 경우 `mel`(melanoma)과 `nv`, `bkl` 사이의 혼동이나 melanoma false negative 같은 중요한 실패 패턴이 전체 지표에 가려질 수 있습니다.

검증 질문:
1. ConvNeXt가 충분한 baseline을 제공하는가?
2. Class imbalance가 실제 성능 병목인가?
3. OVR Expert / Ensemble / Cascade가 melanoma sensitivity를 개선하는가?
4. Temperature Scaling과 class-wise threshold가 calibration과 decision rule을 개선하는가?
5. Metadata 효과가 5-Fold OOF에서도 유지되는가?

## 2. Dataset

**HAM10000 — Human Against Machine with 10000 training images**

7 classes: `akiec`, `bcc`, `bkl`, `df`, `mel`, `nv`, `vasc`

## 3. Experimental Approach

### 3.1 ConvNeXt Baseline & Transfer Learning

ConvNeXt를 중심으로 transfer learning을 수행하고 Accuracy / Macro-AUROC와 함께 class-wise Precision / Recall / F1, Confusion Matrix, melanoma false negative, `mel → nv`, `nv → mel`을 확인했습니다.

### 3.2 Imbalance & Ensemble Experiments

다음 방법을 비교했습니다.

- WeightedRandomSampler
- Focal Loss
- Class-Balanced Loss
- OVR Expert / OVR Soft Ensemble
- Logistic / Ridge Stacking
- Weighted / Soft Ensemble
- Cascade Expert

복잡도 증가보다 실제 validation metric과 class-level failure 개선 여부를 기준으로 평가했습니다. 일부 imbalance / ensemble 방법은 일관된 Macro-AUROC 개선으로 이어지지 않았습니다.

## 4. Calibration & Decision Rule

5-Fold OOF metadata model에서 Temperature Scaling을 평가했습니다.

| Metric | Before | After |
|---|---:|---:|
| Accuracy | 0.8595 | 0.8595 |
| Macro-AUROC | 0.9727 | 0.9727 |
| NLL | 0.3903 | **0.3894** |
| ECE | 0.0136 | **0.0102** |

Temperature Scaling 이후 Accuracy는 유지되었고 NLL과 ECE가 소폭 개선되었습니다. 이를 ranking 변경이 아닌 probability calibration 단계로 해석했습니다.

## 5. Melanoma Threshold Optimization

Calibrated OOF probability에서 melanoma threshold를 sweep했습니다. 선택된 threshold는 **0.30**입니다.

| Metric | Default | mel threshold 0.30 |
|---|---:|---:|
| Accuracy | **0.8595** | 0.8546 |
| Macro-AUROC | 0.9727 | 0.9727 |
| mel Precision | **0.6762** | 0.5994 |
| mel Recall | 0.5930 | **0.7125** |
| mel F1 | 0.6319 | **0.6511** |
| mel False Negative | 453 | **320** |
| mel → nv | 347 | **241** |
| nv → mel | **167** | 323 |

Melanoma Recall은 **0.5930 → 0.7125**, false negative는 **453 → 320**으로 감소했습니다. 반면 `nv → mel` false positive는 **167 → 323**으로 증가했습니다.

따라서 threshold 변경은 ranking 성능 향상이 아니라 false negative 감소를 우선하는 **screening-oriented operating point**로 해석했습니다.

## 6. 5-Fold OOF Generalization Validation

| Fold | Accuracy | Macro-AUROC |
|---|---:|---:|
| 1 | 0.8742 | 0.9796 |
| 2 | 0.8557 | 0.9704 |
| 3 | 0.8602 | 0.9749 |
| 4 | 0.8527 | 0.9754 |
| 5 | 0.8547 | 0.9765 |

OOF 전체 결과:

| Metric | Result |
|---|---:|
| Accuracy | 0.8595 |
| Macro-AUROC | 0.9727 |
| mel Precision | 0.6762 |
| mel Recall | 0.5930 |
| mel F1 | 0.6319 |

Single validation split의 높은 결과보다 OOF 결과를 더 보수적인 generalization estimate로 사용했습니다.

## 7. Metadata & Cost-Sensitive Learning

Image feature에 age / sex / localization metadata를 결합했습니다.

Single validation split의 ConvNeXt + metadata:

| Metric | Result |
|---|---:|
| Accuracy | 0.9076 |
| Macro-AUROC | 0.9893 |
| mel Precision | 0.7674 |
| mel Recall | 0.7399 |
| mel F1 | 0.7534 |

Cost-sensitive learning 추가 결과:

| Metric | Result |
|---|---:|
| Accuracy | 0.9151 |
| Macro-AUROC | 0.9887 |
| mel Precision | 0.7572 |
| mel Recall | **0.8251** |
| mel F1 | **0.7897** |

melanoma sensitivity가 증가했지만 single validation split 결과이므로 최종 일반화 성능으로 간주하지 않았고, 이후 5-Fold OOF로 metadata model을 재평가했습니다.

## 8. Key Findings

- 높은 Macro-AUROC가 minority-class 성능을 보장하지 않았습니다.
- Class imbalance는 유일한 병목이 아니었으며 class confusion, calibration, decision rule을 함께 분석할 필요가 있었습니다.
- 복잡한 ensemble이 항상 더 좋은 Macro-AUROC를 만들지는 않았습니다.
- Temperature Scaling과 threshold optimization은 각각 calibration과 decision rule이라는 다른 문제를 다룹니다.
- Melanoma threshold 조정은 false negative 감소와 false positive 증가 사이의 명확한 trade-off를 만들었습니다.
- Single split 결과를 그대로 일반화하지 않고 5-Fold OOF 결과를 더 보수적인 추정치로 사용했습니다.

## 9. Repository Structure

```text
.
├── kaggle_sim_notebook706b5506c8.ipynb
├── DEVELOPMENT_HISTORY.md
├── oof_metadata_fold_summary.csv
├── oof_metadata_calibration_threshold_summary.csv
├── oof_metadata_calibration_threshold_comparison.csv
├── oof_metadata_mel_threshold_sweep.csv
├── oof_metadata_predictions.csv
├── scripts/
│   ├── build_ham10000_html_report.py
│   ├── build_ham10000_pdf_direct.py
│   ├── build_ham10000_report.py
│   └── build_ham10000_story_report.py
├── pyproject.toml
└── uv.lock
```

## 10. Reproducibility

Original HAM10000 image data와 trained model checkpoint는 저장소에 포함하지 않습니다.

저장소에는 Fold performance, Temperature Scaling, Calibration, Melanoma threshold sweep, Class-level error analysis를 재확인할 수 있는 OOF 결과 파일이 포함되어 있습니다.

Python 환경 정보는 `pyproject.toml`과 `uv.lock`에 기록되어 있습니다.

## 11. Limitations

- 외부 의료기관 데이터에 대한 external validation은 수행하지 않았습니다.
- HAM10000 metadata에는 dataset-specific / acquisition-related bias가 존재할 수 있습니다.
- 일부 실험은 초기 단계에서 single validation split으로 평가했습니다.
- Threshold optimization은 sensitivity를 높이는 대신 false positive를 증가시킬 수 있습니다.
- 본 프로젝트의 결과는 의료 진단 성능을 의미하지 않습니다.

## Tech Stack

`Python` · `PyTorch` · `ConvNeXt` · `scikit-learn` · `pandas` · `matplotlib` · `Grad-CAM` · `LIME`

## Author

**Sungmin Oh**

GitHub: [@fabxoe](https://github.com/fabxoe)
