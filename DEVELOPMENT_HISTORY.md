# HAM10000 ConvNeXt Development History

## 2026-07-07

### Git Project Setup

- Initialized this folder as a Git project.
- Added `.gitignore` to exclude local virtual environments, cache files, temporary folders, and reproducible PDF render QA images.

### Report Revision: OVR Expert And Ensemble Section

- Started from the latest report lineage around `HAM10000_ConvNeXt_보고서_HTML_20260707_1554.html`.
- Generated updated report outputs:
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1632.html`
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1632.pdf`
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1643.html`
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1643.pdf`

### Added OVR Auxiliary Chart

- Kept the existing `mel precision-recall trade-off by OVR blending` chart as the main OVR insight.
- Added `report_assets/chart_ovr_macro_recall.png` as an auxiliary chart for OVR alpha analysis.
- The auxiliary chart shows that increasing OVR Expert weight raises melanoma recall while Macro-AUROC slightly decreases.
- Updated figure numbering:
  - Figure 3: mel precision-recall trade-off by OVR blending
  - Figure 4: Macro-AUROC and mel recall auxiliary comparison by OVR alpha
  - Figure 5: Temperature Scaling NLL/ECE comparison
  - Figure 6: Threshold recall/F1 comparison

### Clarified Section 6 vs Section 7

- Revised Section 6 so readers do not confuse OVR soft blending with threshold optimization.
- Section 6 is now framed as a probability blending experiment:
  - ConvNeXt melanoma probability is combined with OVR Expert probability.
  - Higher alpha improves melanoma recall but can reduce precision and Macro-AUROC.
  - OVR Soft Ensemble is interpreted as a melanoma sensitivity support experiment, not as a broadly superior final model.
- Section 7 is kept as a separate analysis:
  - Temperature Scaling adjusts probability calibration.
  - Class-wise threshold optimization adjusts the decision rule after probabilities are produced.

### Chart Styling Improvement

- Regenerated `chart_ovr_macro_recall.png` with thicker lines, larger markers, larger legend text, and larger axis/title fonts.
- Matched the visual style of Figure 4 more closely to Figure 3 for consistency in the report.

### PDF Generation And QA

- Generated PDF from HTML using Playwright Chromium.
- Confirmed all pages are A4 portrait:
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1632.pdf`: 10 pages, all portrait
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1643.pdf`: 10 pages, all portrait
- Rendered PDF pages to PNG during QA and inspected the OVR/Ensemble section.
- Fixed table splitting behavior so rows are less likely to break awkwardly across pages.

### Current Recommended Report Version

- Use `HAM10000_ConvNeXt_보고서_HTML_20260707_1643.html` and `HAM10000_ConvNeXt_보고서_HTML_20260707_1643.pdf` as the latest refined version.

### Clinical Metadata Multimodal Result Update

- Reviewed the updated Kaggle notebook section:
  - `17. HAM10000 ConvNeXt + Clinical Metadata Multimodal Experiment`
- Confirmed the ConvNeXt feature extraction bug was fixed by replacing only the final classifier linear layer:
  - `self.backbone.classifier[2] = nn.Identity()`
  - This keeps ConvNeXt output as `[B, 768]`, allowing concatenation with metadata MLP output `[B, 64]`.
- Recorded the multimodal validation result:
  - Accuracy: `0.9076`
  - Macro-AUROC: `0.989303`
  - melanoma precision: `0.7674`
  - melanoma recall: `0.7399`
  - melanoma F1: `0.7534`
  - melanoma AUROC: `0.968491`
- Added `report_assets/chart_metadata_multimodal.png` to compare baseline vs ConvNeXt + metadata on Accuracy, Macro-AUROC, mel Recall, and mel F1.
- Updated the report with a new section:
  - `8. 임상 메타데이터 결합 추가 실험`
- Kept the interpretation cautious:
  - The result suggests a meaningful improvement trend.
  - It is not treated as a final conclusion because it comes from a single validation split and may reflect metadata or data collection bias.
- Generated updated report outputs:
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1813.html`
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1813.pdf`
- Verified the PDF:
  - 12 pages
  - all A4 portrait
  - metadata section and final conclusion render without awkward page overflow.

### Current Recommended Report Version

- Use `HAM10000_ConvNeXt_보고서_HTML_20260707_1813.html` and `HAM10000_ConvNeXt_보고서_HTML_20260707_1813.pdf` as the latest refined version.

### Cost-Sensitive Learning Result

- Added and reviewed notebook section:
  - `18. Cost-Sensitive Learning Experiment(ConvNeXt + Metadata)`
- Experiment setup:
  - Base model: `ConvNeXt + age/sex/localization metadata`
  - Loss: `CostSensitiveCrossEntropy`
  - `MEL_FN_COST = 3.0`
  - `MEL_TO_NV_COST = 5.0`
  - `COST_LAMBDA = 0.5`
  - Selection score: `Macro-AUROC + 0.1 * mel recall`
- Best epoch:
  - Epoch: `5`
  - Train loss: `0.198756`
  - Train accuracy: `0.954194`
  - Validation loss: `0.374999`
  - Validation accuracy: `0.915127`
  - Validation Macro-AUROC: `0.988742`
  - melanoma precision: `0.757202`
  - melanoma recall: `0.825112`
  - melanoma F1: `0.789700`
  - melanoma AUROC: `0.970157`
  - melanoma FN total: `39`
  - melanoma -> nv errors: `26`
  - Saved model: `convnext_metadata_cost_sensitive_best.pth`
- Final classification report summary:

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| akiec | 0.7143 | 0.8462 | 0.7746 | 65 |
| bcc | 0.8812 | 0.8641 | 0.8725 | 103 |
| bkl | 0.8821 | 0.7818 | 0.8289 | 220 |
| df | 0.8696 | 0.8696 | 0.8696 | 23 |
| mel | 0.7572 | 0.8251 | 0.7897 | 223 |
| nv | 0.9641 | 0.9605 | 0.9623 | 1341 |
| vasc | 0.8929 | 0.8929 | 0.8929 | 28 |

- Confusion matrix highlights:
  - True melanoma samples: `223`
  - Correct melanoma predictions: `184`
  - melanoma false negatives: `39`
  - melanoma -> nv: `26`
  - nv -> melanoma: `37`
- Class-wise AUROC:

| Class | AUROC |
|---|---:|
| akiec | 0.995054 |
| bcc | 0.995294 |
| bkl | 0.980207 |
| df | 0.997211 |
| mel | 0.970157 |
| nv | 0.983829 |
| vasc | 0.999439 |

### Cost-Sensitive Learning Interpretation

- Compared with the previous `ConvNeXt + metadata` result:

| Model | Accuracy | Macro-AUROC | mel Precision | mel Recall | mel F1 | mel AUROC |
|---|---:|---:|---:|---:|---:|---:|
| ConvNeXt + metadata | 0.9076 | 0.989303 | 0.7674 | 0.7399 | 0.7534 | 0.968491 |
| Metadata + Cost-Sensitive | 0.9151 | 0.988742 | 0.7572 | 0.8251 | 0.7897 | 0.970157 |

- Main insight:
  - Cost-sensitive learning substantially improved melanoma recall from `0.7399` to `0.8251`.
  - melanoma F1 also improved from `0.7534` to `0.7897`.
  - Macro-AUROC slightly decreased from `0.989303` to `0.988742`, so the result should be interpreted as a melanoma-sensitivity improvement rather than a clear overall ranking-performance gain.
  - The result is clinically meaningful for a screening-oriented model because melanoma false negatives decreased, but nv -> melanoma false positives should still be monitored.

### Cost Weight Sweep Notes

- Planned next step:
  - Run a cost-weight sweep over `MEL_FN_COST`, `MEL_TO_NV_COST`, and `COST_LAMBDA`.
- Runtime issue encountered:
  - A 2-GPU `DataParallel` version caused GPU memory pressure in Kaggle.
  - A later sweep attempt failed because `train_ds` was not defined in the notebook state.
- Follow-up code direction:
  - Use a 1-GPU standalone sweep cell that rebuilds metadata preprocessing, dataset, dataloaders, and the model inside the cell.
  - Keep `BATCH_SIZE = 32` by default.
  - If memory remains unstable, reduce to `BATCH_SIZE = 16` and reduce sweep configs to 2 candidates.

### Report Update: Cost-Sensitive Learning

- Updated the report to include the completed cost-sensitive learning result.
- Expanded the metadata comparison table to include:
  - `Metadata + cost-sensitive`
  - Accuracy: `0.9151`
  - Macro-AUROC: `0.988742`
  - melanoma precision: `0.7572`
  - melanoma recall: `0.8251`
  - melanoma F1: `0.7897`
- Updated `report_assets/chart_metadata_multimodal.png` to compare:
  - ConvNeXt baseline
  - ConvNeXt + metadata
  - Metadata + cost-sensitive
- Added a new report section:
  - `9. Cost-Sensitive Learning 추가 실험`
- Added cost-sensitive class-wise AUROC table:
  - akiec: `0.995054`
  - bcc: `0.995294`
  - bkl: `0.980207`
  - df: `0.997211`
  - mel: `0.970157`
  - nv: `0.983829`
  - vasc: `0.999439`
- Updated the conclusion to state that cost-sensitive learning improved melanoma recall to `0.8251`, while keeping the interpretation cautious because the result is still based on a single validation split.
- Generated updated report outputs:
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1941.html`
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_1941.pdf`
- Verified the PDF:
  - 13 pages
  - all A4 portrait
  - cost-sensitive section, summary table, and conclusion render correctly.

### Current Recommended Report Version

- Use `HAM10000_ConvNeXt_보고서_HTML_20260707_1941.html` and `HAM10000_ConvNeXt_보고서_HTML_20260707_1941.pdf` as the latest refined version.

### Report Image Rendering Fix

- Updated report image CSS in `scripts/build_ham10000_html_report.py`.
- Changed chart rendering behavior:
  - Removed fixed `max-height: 310px`.
  - Added `height: auto`.
  - Added `max-width: 100%`.
  - Added `break-inside: avoid`.
- Purpose:
  - Prevent charts from appearing clipped or vertically compressed in the HTML/PDF output.
  - Preserve chart aspect ratio across browser view and PDF rendering.
- Generated updated report outputs:
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_2033.html`
  - `HAM10000_ConvNeXt_보고서_HTML_20260707_2033.pdf`
- Verified the PDF:
  - 13 pages
  - all A4 portrait
  - OVR charts and metadata/cost-sensitive comparison chart render without image clipping.

### Current Recommended Report Version

- Use `HAM10000_ConvNeXt_보고서_HTML_20260707_2033.html` and `HAM10000_ConvNeXt_보고서_HTML_20260707_2033.pdf` as the latest refined version.

### Standalone HTML Embedding Fix

- Updated `scripts/build_ham10000_html_report.py` so report images are embedded directly into the HTML as Base64 data URIs.
- Purpose:
  - Make the HTML distributable outside the project folder.
  - Remove dependency on `report_assets/` or local `file://` image paths.
- Verification:
  - Generated HTML contained `data:image/png;base64,...` image sources.
  - No `file://` references remained.

### Conservative Cascade Expert Result

- Added a conservative cascade follow-up after the aggressive Cascade Expert trial.
- Baseline:
  - Accuracy: `0.847728`
  - Macro-AUROC: `0.969942`
  - melanoma precision: `0.692771`
  - melanoma recall: `0.515695`
  - melanoma F1: `0.591260`
  - melanoma FN: `108`
  - mel -> nv: `87`
  - nv -> mel: `35`
- Aggressive Cascade:
  - Accuracy: `0.804793`
  - Macro-AUROC: `0.968767`
  - melanoma precision: `0.438596`
  - melanoma recall: `0.784753`
  - melanoma F1: `0.562701`
  - melanoma FN: `48`
  - mel -> nv: `39`
  - nv -> mel: `146`
- Conservative Cascade selected operating point:
  - mode: `score_boost`
  - gate threshold: `0.20`
  - expert threshold: `0.50`
  - boost alpha: `0.40`
- Conservative Cascade result:
  - Accuracy: `0.849725`
  - Macro-AUROC: `0.970140`
  - melanoma precision: `0.645161`
  - melanoma recall: `0.627803`
  - melanoma F1: `0.636364`
  - melanoma FN: `83`
  - mel -> nv: `69`
  - nv -> mel: `52`
- Interpretation:
  - Aggressive Cascade reduced melanoma FN strongly but caused excessive nv -> mel false positives.
  - Conservative Cascade preserved overall Accuracy/Macro-AUROC while reducing melanoma FN by `25` and mel -> nv errors by `18`.
  - melanoma precision decreased and nv -> mel errors increased, so this should be described as a screening-oriented operating point rather than a diagnostic improvement.

### Report Update: Conservative Cascade + Single-File HTML

- Generated new chart:
  - `report_assets/chart_conservative_cascade.png`
- Updated report section `6. Expert Model과 Ensemble` with:
  - `6.1 Cascade Expert 운영점 보수화`
  - aggressive vs conservative cascade comparison table
  - conservative cascade bar chart
  - cautious screening-oriented interpretation
- Updated summary/ranking/conclusion sections to include Conservative Cascade.
- Generated updated standalone report outputs:
  - `HAM10000_ConvNeXt_보고서_HTML_20260708_0206.html`
  - `HAM10000_ConvNeXt_보고서_HTML_20260708_0206.pdf`
- Verification:
  - HTML contains `8` embedded Base64 images.
  - No `file://` or external `.png` references remain.
  - PDF rendered as `15` A4 portrait pages.
  - QA render directory: `qa_render/html_pdf_0206`.
  - Checked chart-heavy pages and confirmed images are not clipped.

### Current Recommended Report Version

- Use `HAM10000_ConvNeXt_보고서_HTML_20260708_0206.html` as the deployable standalone HTML report.
- Use `HAM10000_ConvNeXt_보고서_HTML_20260708_0206.pdf` when a fixed portrait PDF is needed.

### 5-Fold OOF Metadata Calibration/Threshold Result

- Imported Kaggle OOF result files:
  - `oof_metadata_fold_summary.csv`
  - `oof_metadata_calibration_threshold_summary.csv`
  - `oof_metadata_calibration_threshold_comparison.csv`
  - `oof_metadata_mel_threshold_sweep.csv`
  - `oof_metadata_predictions.csv`
- Fold-wise results:
  - Fold 1: Accuracy `0.8742`, Macro-AUROC `0.9796`
  - Fold 2: Accuracy `0.8557`, Macro-AUROC `0.9704`
  - Fold 3: Accuracy `0.8602`, Macro-AUROC `0.9749`
  - Fold 4: Accuracy `0.8527`, Macro-AUROC `0.9754`
  - Fold 5: Accuracy `0.8547`, Macro-AUROC `0.9765`
- OOF raw metadata model:
  - Accuracy: `0.859511`
  - Macro-AUROC: `0.972677`
  - melanoma precision: `0.676230`
  - melanoma recall: `0.592992`
  - melanoma F1: `0.631881`
  - melanoma FN: `453`
  - mel -> nv: `347`
  - nv -> mel: `167`
- OOF Temperature Scaling:
  - Temperature: `1.061248`
  - NLL: `0.390324 -> 0.389447`
  - ECE: `0.013621 -> 0.010187`
  - Accuracy unchanged at `0.859511`
  - Macro-AUROC: `0.972677 -> 0.972742`
- OOF calibrated mel threshold:
  - Best threshold: `0.30`
  - Accuracy: `0.854618`
  - melanoma precision: `0.599395`
  - melanoma recall: `0.712489`
  - melanoma F1: `0.651067`
  - melanoma FN: `320`
  - mel -> nv: `241`
  - nv -> mel: `323`
- Interpretation:
  - Metadata model retained strong OOF Macro-AUROC, but below the single validation split result, so OOF should be treated as the more conservative generalization estimate.
  - Temperature Scaling produced a small but consistent calibration improvement in OOF.
  - mel thresholding reduced melanoma FN and mel -> nv errors, but substantially increased nv -> mel false positives.

### Report Update: OOF Generalization Section

- Added `uv` package management files and installed analysis packages:
  - `pandas`
  - `matplotlib`
- Generated new report assets:
  - `report_assets/chart_oof_fold_performance.png`
  - `report_assets/chart_oof_metadata_validation.png`
- Added report section:
  - `10. 5-Fold OOF 일반화 검증`
- Added tables for:
  - fold-wise OOF performance
  - OOF calibration/threshold comparison
  - top mel threshold candidates
- Updated summary/ranking/conclusion with OOF generalization findings.
- Generated updated standalone report outputs:
  - `HAM10000_ConvNeXt_보고서_HTML_20260708_0327.html`
  - `HAM10000_ConvNeXt_보고서_HTML_20260708_0327.pdf`
- Verification:
  - HTML contains `10` embedded Base64 images.
  - No `file://` or external `.png` references remain.
  - PDF was generated from the standalone HTML.

### Current Recommended Report Version

- Use `HAM10000_ConvNeXt_보고서_HTML_20260708_0327.html` as the latest deployable standalone HTML report.
- Use `HAM10000_ConvNeXt_보고서_HTML_20260708_0327.pdf` as the latest fixed portrait PDF.

### Story-Style Report Version

- User feedback:
  - The quantitative report preserved the data, but read like a dense paper with insufficient narrative flow.
- Added a separate story-oriented report generator:
  - `scripts/build_ham10000_story_report.py`
- Report structure:
  - Starts from the central question: beyond AUROC, how can melanoma misses be reduced?
  - Reframes experiments as a sequence of questions:
    - Is the baseline strong enough?
    - Is class imbalance the main bottleneck?
    - Can melanoma be supported by an OVR expert?
    - Can cascade reduce misses without excessive false positives?
    - Can calibration/threshold make the decision rule more clinically useful?
    - Does metadata help?
    - Does the effect remain under 5-Fold OOF validation?
- Design changes:
  - Added stronger title and lead.
  - Added metric cards for OOF AUROC, ECE, and mel FN reduction.
  - Added highlight and caution callouts.
  - Reduced dense table-first style.
  - Kept medical interpretation cautious: screening-oriented support, not diagnostic claim.
- Generated story report outputs:
  - `HAM10000_ConvNeXt_스토리형보고서_20260708_0335.html`
  - `HAM10000_ConvNeXt_스토리형보고서_20260708_0335.pdf`
- Verification:
  - HTML contains `10` embedded Base64 images.
  - No `file://` or external `.png` references remain.
  - PDF rendered as `12` A4 portrait pages.
  - QA render directory: `qa_render/story_pdf_0335`.
