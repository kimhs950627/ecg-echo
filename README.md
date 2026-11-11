# ECG → Echo Report

EchoNext 공개 파형(100,000 ECG)을 GE MAC5K 결과지 레이아웃으로 렌더해 만든 이미지 데이터셋과,
그 이미지에서 심초음파 12개 라벨을 예측하는 모델의 EDA·데모·학습 전략을 담은 정적 사이트입니다.

- 표지 · EDA 리포트 · 데모 · 학습 전략 4개 페이지
- 모든 수치는 `tools/make_eda.py` 가 metadata 를 직접 집계한 결과 (`data/summary.json`)
- 페이지는 `tools/build_site.py` 가 summary.json 으로 생성

## 구조

```
index.html            표지
eda.html              Tab 1 — Metadata EDA
demo.html             Tab 2 — 웹 데모 (모델 미배포 상태)
plan.html             Tab 3 — 학습 전략
styles/               tokens.css (clay-sand 테마) + site.css
assets/figures/       EDA 그림 (png 원본 + webp 배포본)
assets/samples/       렌더된 결과지 샘플 3장
data/summary.json     EDA 집계 결과 (공개 가능한 수치만)
tools/make_eda.py     metadata.csv → 그림 + summary.json
tools/build_site.py   summary.json → html 4장 + 404/robots/sitemap
```

## 재현

```bash
pip install pandas numpy matplotlib pillow
python3 tools/make_eda.py --meta metadata.csv --out assets/figures --summary data/summary.json
python3 tools/build_site.py
```

## 공개 범위

- 원본 파형 npy, patient-level metadata.csv, 모델 가중치는 이 저장소에 없습니다(집계 수치만 공개).
- 연구·교육 목적. 의료적 진단을 대신하지 않습니다.

## 출처

- 데이터: EchoNext (PhysioNet, Elias & Finer) — <https://physionet.org/content/echonext>
- 렌더 파이프라인: `npy_to_ekg.py` (별도 private Kaggle dataset `khs224025/ecg-render-code`)
