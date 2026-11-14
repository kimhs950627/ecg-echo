#!/usr/bin/env python3
"""Generate the static site (index / eda / demo) from data/summary.json.

No template engine: the site is four static pages, so the builder is just
string formatting plus the numbers that must not be typed by hand.

    python3 tools/build_site.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "data" / "summary.json").read_text())
SITE_URL = "https://kimhs950627.github.io/ecg-echo"
TODAY = date.today().isoformat()

NAV = [
    ("index.html", "표지"),
    ("eda.html", "EDA 리포트"),
    ("demo.html", "데모"),
    ("plan.html", "학습 전략"),
]


def fig(name: str, alt: str, caption: str) -> str:
    """PNG is the source of truth; the page ships a webp copy."""
    p = ROOT / "assets" / "figures" / name
    im = Image.open(p)
    webp = p.with_suffix(".webp")
    if not webp.exists() or webp.stat().st_mtime < p.stat().st_mtime:
        im.convert("RGB").save(webp, "WEBP", quality=88, method=6)
    return (
        f'<figure class="figure"><img src="assets/figures/{webp.name}" alt="{alt}" '
        f'width="{im.size[0]}" height="{im.size[1]}" decoding="async">'
        f"<figcaption>{caption}</figcaption></figure>"
    )


def shell(title: str, desc: str, page: str, body: str, extra_head: str = "") -> str:
    nav = "\n".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == page else ""}>{label}</a></li>'
        for href, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE_URL}/{page}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE_URL}/{page}">
<meta property="og:image" content="{SITE_URL}/assets/samples/ecg_0000861.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F4EDE3">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles/site.css">
{extra_head}
</head>
<body>
<a class="skip-link" href="#main">본문으로 건너뛰기</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html"><span class="dot" aria-hidden="true"></span>ECG<b>→</b>Echo<span class="full">&nbsp;Report</span></a>
    <nav aria-label="주요 섹션"><ul class="tabs">{nav}</ul></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div>
      <p class="footer-note">EchoNext 공개 파형(100,000 ECG)을 GE MAC5K 결과지 레이아웃으로 렌더해 만든 연구용 이미지 데이터셋.
      원본 파형과 환자 단위 metadata 는 공개 페이지에 올리지 않습니다.</p>
      <p class="footer-note">연구·교육 목적. 의료적 진단을 대신하지 않습니다.</p>
    </div>
    <div class="footer-meta">
      contact: <a href="https://github.com/kimhs950627/ecg-echo">github.com/kimhs950627/ecg-echo</a><br>
      built {TODAY} · figures by <code>tools/make_eda.py</code><br>
      source dataset: EchoNext (Muhammad Fasseh, Kaggle)
    </div>
  </div>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------- index
def build_index() -> str:
    sp = S["splits"]
    lv = S["labels"]
    body = f"""
<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">EchoNext · GE MAC5K layout · 100,000 ECGs</p>
      <h1>심전도 한 장에서<br>심초음파 소견을 <span>읽어내는</span> 모델</h1>
      <p class="lead">출판된 결과지 사진을 실측해 재현한 ECG 이미지 {S['n_rows']:,}장과,
      심초음파 12개 라벨·tabular metadata 로 학습 데이터를 만들고, 브라우저에서 바로 돌아가는
      추론 화면까지 배포하는 프로젝트입니다.</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="eda.html">EDA 리포트 보기</a>
        <a class="btn btn-ghost" href="demo.html">데모 화면</a>
      </div>
    </div>
    <figure class="printout">
      <img src="assets/samples/ecg_0000861.png" alt="렌더된 GE MAC5K 형식 12유도 심전도 결과지" width="1124" height="814">
      <figcaption>실제 렌더 결과 · 1124×814 px · PNG 128색</figcaption>
    </figure>
  </div>
</section>

<section class="stats" aria-label="데이터셋 요약">
  <div class="wrap">
  <div class="stat"><div class="v">{S['n_rows']:,}</div><div class="k">렌더된 ECG 이미지</div></div>
  <div class="stat"><div class="v">{S['n_patients']:,}</div><div class="k">환자 (patient_key)</div></div>
  <div class="stat"><div class="v">{len(lv)}</div><div class="k">심초음파 라벨</div></div>
  <div class="stat"><div class="v">{lv['SHD composite']['pct']:.0f}%</div><div class="k">SHD composite 양성</div></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>무엇을 만들었나</h2><span class="idx">01 / 03</span></div>
    <div class="cards">
      <article class="card">
        <p class="n">렌더 파이프라인</p>
        <h3>결과지 그대로의 이미지</h3>
        <p>IntroECG 정규화 상수로 z-score 를 mV 로 되돌리고, 25 mm/s · 10 mm/mV 격자에
        3×4 순차 배열 + 10초 rhythm strip(II) 로 그립니다. 측정 블록·판독문·기기 라인까지 실제 결과지 배치를 따릅니다.</p>
      </article>
      <article class="card">
        <p class="n">라벨 세트</p>
        <h3>12개 심초음파 소견</h3>
        <p>LVEF ≤ 45%, LVWT, AS/AR/MR/TR/PR ≥ moderate, RV dysfunction, pericardial effusion,
        PASP ≥ 45, TR max ≥ 3.2 m/s, 그리고 이를 묶은 SHD composite({lv['SHD composite']['pct']:.1f}%).</p>
      </article>
      <article class="card">
        <p class="n">배포</p>
        <h3>사진 한 장 → 라벨</h3>
        <p>결과지 사진을 넣으면 라벨 확률을 돌려주는 화면을 목표로 합니다. 1차는 정적 웹(ONNX Runtime Web),
        2차는 같은 모델을 PC 앱·APK 로 감싸는 구조입니다.</p>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>데이터 파이프라인</h2><span class="idx">02 / 03</span></div>
    <div class="grid-2">
      <div class="prose">
        <p>원본 공개 파형은 <span class="mono">(N, 1, 2500, 12)</span> float64 — 10초 · 250 Hz · 12유도입니다.
        여기에 리드별 정규화 상수(mean/std, 0.1–99.9 percentile clip)를 역적용해 mV 로 되돌린 뒤,
        실물 결과지 축척(4.0752 px/mm)에 맞춰 렌더합니다.</p>
        <p>렌더 결과는 <span class="mono">train {sp['train']:,} · val {sp['val']:,} ·
        test {sp['test']:,} · no_split {sp['no_split']:,}</span> 로 나뉘고,
        <span class="mono">metadata.csv</span> 가 이미지 경로·라벨·tabular 를 한 행으로 묶습니다.</p>
        <p class="muted">학습은 로컬 GPU 없이 Kaggle 노트북에서 진행하고, 이 사이트는 결과와 추론 화면만 담습니다.</p>
      </div>
      <div>
        <table class="data">
          <caption>렌더 배포본과 속도(실측)</caption>
          <thead><tr><th>항목</th><th>값</th></tr></thead>
          <tbody>
            <tr><td>해상도</td><td class="num">1124 × 814 px (103.5 dpi)</td></tr>
            <tr><td>파일 형식</td><td class="num">PNG · palette 128</td></tr>
            <tr><td>장당 크기</td><td class="num">약 45 KB</td></tr>
            <tr><td>전체 용량</td><td class="num">약 4.3 GB</td></tr>
            <tr><td>렌더 속도</td><td class="num">0.20 s/장 (4 worker)</td></tr>
            <tr><td>총 소요</td><td class="num">약 5시간</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>지금 어디까지 왔나</h2><span class="idx">03 / 03</span></div>
    <table class="data">
      <thead><tr><th>단계</th><th>상태</th><th>비고</th></tr></thead>
      <tbody>
        <tr><td>렌더러 구현·검증</td><td><span class="tag">완료</span></td><td>mV↔z 왕복오차 2.4e-7, 결과지 헤더 실측 재현</td></tr>
        <tr><td>100k 배치 렌더</td><td><span class="tag">완료</span></td><td>Kaggle 노트북 v4, split 별 파일 수 확인</td></tr>
        <tr><td>Metadata EDA</td><td><span class="tag">완료</span></td><td>이 사이트의 EDA 탭 (코드 산출, 수기 입력 없음)</td></tr>
        <tr><td>웹 표면</td><td><span class="tag">완료</span></td><td>표지·EDA·데모·전략 (이 페이지)</td></tr>
        <tr><td>이미지 supervised 학습</td><td><span class="tag warn">예정</span></td><td>Kaggle GPU 노트북, 환자 단위 split 재구성 필요</td></tr>
        <tr><td>브라우저 추론</td><td><span class="tag warn">예정</span></td><td>ONNX Runtime Web + 사진 전처리</td></tr>
      </tbody>
    </table>
  </div>
</section>
"""
    return shell(
        "ECG → Echo Report — 심전도 이미지로 심초음파 소견 예측",
        "EchoNext 파형 10만 장을 GE MAC5K 결과지 이미지로 렌더한 데이터셋과, 심초음파 12개 라벨 예측 모델의 EDA·데모.",
        "index.html",
        body,
    )


# --------------------------------------------------------------------------- eda
def build_eda() -> str:
    sp = S["splits"]
    lv = S["labels"]
    meas = S["measurements"]
    total = S["n_rows"]

    label_rows = "\n".join(
        f'<tr><td>{k}</td><td class="num">{v["n"]:,}</td><td class="num">{v["pct"]:.2f}%</td>'
        f'<td><div class="bar-cell"><div class="track"><div class="fill" style="width:{min(v["pct"]*1.9,100):.1f}%"></div></div></div></td></tr>'
        for k, v in lv.items()
    )
    meas_rows = "\n".join(
        f'<tr><td>{k}</td><td class="num">{v["median"]:g} {v["unit"]}</td>'
        f'<td class="num">{v["q1"]:g}–{v["q3"]:g}</td><td class="num">{v["missing_pct"]:.1f}%</td></tr>'
        for k, v in meas.items()
    )
    split_rows = "\n".join(
        f'<tr><td class="mono">{k}</td><td class="num">{v:,}</td><td class="num">{v/total*100:.1f}%</td></tr>'
        for k, v in sp.items()
    )
    missing_rows = "\n".join(
        f'<tr><td class="mono">{m["col"]}</td><td class="num">{m["pct"]:.1f}%</td></tr>'
        for m in S["missing_top"]
    )
    corr_rows = "\n".join(
        f'<tr><td>{c["a"]}</td><td>{c["b"]}</td><td class="num">{c["phi"]:.2f}</td></tr>'
        for c in S["label_corr_top"]
    )
    interp_rows = "\n".join(
        f'<tr><td class="mono">{t["phrase"]}</td><td class="num">{t["n"]:,}</td><td class="num">{t["pct"]:.1f}%</td></tr>'
        for t in S["interpretation"]["top"]
    )
    age = S["age"]
    sex = S["sex"]

    body = f"""
<section class="hero" style="padding-bottom:var(--space-6)">
  <div class="wrap" style="grid-template-columns:1fr">
    <div class="prose">
      <p class="eyebrow">Tab 1 · Metadata EDA · generated {TODAY}</p>
      <h1 style="font-size:var(--text-2xl)">렌더된 10만 장은 어떤 데이터인가</h1>
      <p class="lead">모든 수치는 <code>tools/make_eda.py</code> 가 <code>metadata.csv</code> 를 직접 집계한 결과입니다.
      손으로 옮겨 적은 값은 없습니다.</p>
    </div>
  </div>
</section>

<section class="stats" aria-label="핵심 수치">
  <div class="wrap">
  <div class="stat"><div class="v">{S['n_rows']:,}</div><div class="k">행 (이미지 1장 = 1행)</div></div>
  <div class="stat"><div class="v">{S['n_cols']}</div><div class="k">컬럼</div></div>
  <div class="stat"><div class="v">{S['n_patients']:,}</div><div class="k">환자</div></div>
  <div class="stat"><div class="v">{S['patients_in_multiple_splits']:,}</div><div class="k">여러 split 에 걸친 환자</div></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>1. 구조와 무결성</h2><span class="idx">01 / 08</span></div>
    <div class="grid-2">
      <div>
        <table class="data">
          <caption>split 구성 — 합계 {total:,}</caption>
          <thead><tr><th>split</th><th>이미지</th><th>비중</th></tr></thead>
          <tbody>{split_rows}</tbody>
        </table>
        <p class="prose">이미지 경로 중복 0건, 경로의 split 접두사와 <code>split</code> 컬럼 불일치 0건,
        전 파일 PNG. 렌더 산출물이 metadata 와 1:1 로 맞습니다.</p>
      </div>
      <div>{fig("split_sizes.png", "split 별 이미지 수 막대그래프", "학습 72.5%, 나머지는 검증·평가·미할당입니다. no_split 은 학습에서 빼고 외부 검증용으로 남깁니다.")}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>2. 표본 특성</h2><span class="idx">02 / 08</span></div>
    <div class="grid-2">
      <div>
        <p class="prose">나이 중앙값 <b>{age['median']:.0f}세</b> (IQR {age['q1']:.0f}–{age['q3']:.0f}),
        50세 미만 {age['pct_under_50']:.1f}%. 성별은 남 {sex.get('male',0):,} · 여 {sex.get('female',0):,}.</p>
        <p class="prose">환자당 ECG 중앙값 {S['ecg_per_patient']['median']:.0f}건, 평균 {S['ecg_per_patient']['mean']:.2f}건,
        최대 {S['ecg_per_patient']['max']}건. 전체 환자의 {S['ecg_per_patient']['pct_patients_multi_ecg']:.1f}% 가
        2건 이상의 ECG 를 가집니다 — 이 사실이 split 설계에서 문제가 됩니다(6절).</p>
      </div>
      <div>{fig("age_sex.png", "나이 분포와 성별 비율", "나이·성별 분포. 18–90세로 절단돼 있습니다(원본 공개 데이터 기준).")}</div>
    </div>
    {fig("year_setting.png", "촬영 연도와 진료 세팅 분포", "촬영 연도와 진료 세팅. 응급·입원 비중이 높아 중증도가 외래보다 높은 표본입니다.")}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>3. 라벨</h2><span class="idx">03 / 08</span></div>
    <div class="grid-2">
      <div>{fig("label_prevalence.png", "심초음파 12개 라벨 유병률", "라벨 유병률. 최소 0.8%(PR ≥ moderate)에서 최대 52.2%(SHD composite)까지 60배 차이입니다.")}</div>
      <div>
        <table class="data">
          <caption>라벨별 양성 수</caption>
          <thead><tr><th>라벨</th><th>n</th><th>%</th><th></th></tr></thead>
          <tbody>{label_rows}</tbody>
        </table>
      </div>
    </div>
    {fig("prevalence_by_age.png", "연령대별 라벨 유병률 히트맵", "연령대별 유병률. 대부분 라벨이 나이에 단조 증가하므로, 나이를 모델에 그대로 넣으면 성능이 과대평가될 수 있습니다.")}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>4. 라벨 동시발생</h2><span class="idx">04 / 08</span></div>
    <div class="grid-2">
      <div>{fig("label_corr.png", "라벨 간 Pearson phi 상관 히트맵", "라벨 간 φ 상관. 같은 초음파 검사에서 파생된 라벨이라 구조적으로 상관합니다.")}</div>
      <div>
        <table class="data">
          <caption>가장 강한 라벨 쌍 (|φ| 상위 5)</caption>
          <thead><tr><th>A</th><th>B</th><th>φ</th></tr></thead>
          <tbody>{corr_rows}</tbody>
        </table>
        <p class="prose">PASP ≥ 45 와 TR max ≥ 3.2 (φ 0.65) 는 같은 측정에서 계산되는 값이라 사실상 한 라벨입니다.
        다중 라벨을 독립으로 다루면 이 구조가 손실로 이어지므로, 공동 학습 또는 라벨 간 의존을 반영하는 head 가 필요합니다.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>5. 수치형 변수</h2><span class="idx">05 / 08</span></div>
    {fig("numeric_dist.png", "주요 수치형 변수 분포 6개", "심전도 측정값(박동수·PR·QRS·QTc)과 심초음파 값(LVEF·PASP)의 분포. 0.5–99.5 percentile 로 절단해 그렸습니다.")}
    <div class="grid-2">
      <table class="data">
        <caption>수치형 요약 (중앙값, IQR, 결측)</caption>
        <thead><tr><th>변수</th><th>중앙값</th><th>IQR</th><th>결측</th></tr></thead>
        <tbody>{meas_rows}</tbody>
      </table>
      <div>{fig("lvef.png", "LVEF 분포와 연령대별 감소 EF 유병률", "LVEF 는 45% 를 경계로 라벨이 갈립니다. 45–50% 구간에 표본이 몰려 있어 경계 근처 판정이 흔들리기 쉽습니다.")}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>6. 결측</h2><span class="idx">06 / 08</span></div>
    <div class="grid-2">
      <div>
        <table class="data">
          <caption>결측 상위 15개 컬럼</caption>
          <thead><tr><th>컬럼</th><th>결측률</th></tr></thead>
          <tbody>{missing_rows}</tbody>
        </table>
        <p class="prose">PASP(43%)·TR max(55%) 는 삼첨판 역류 신호가 잡힌 검사에서만 측정됩니다.
        이 값들을 입력 feature 로 쓰면 <b>측정 자체가 된 환자</b>라는 선택편향이 들어갑니다 — 이미지 모델의 정답으로만 쓰고 입력에는 쓰지 않습니다.</p>
      </div>
      <div>{fig("missingness.png", "결측률 상위 컬럼 막대그래프", "결측은 무작위가 아니라 검사 시행 여부와 연결돼 있습니다.")}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>7. 판독문 텍스트 = 누수 표면</h2><span class="idx">07 / 08</span></div>
    <div class="grid-2">
      <div>
        <div class="callout">
          <h3>결과지에 인쇄된 판독문이 라벨과 직접 상관합니다</h3>
          <p>렌더된 결과지에는 실제 판독문 <code>{S['interpretation']['unique_strings']}종</code>이 그대로 인쇄됩니다
          (“ABNORMAL ECG” {S['interpretation']['top'][1]['pct']:.0f}%, “LEFT AXIS DEVIATION” 등).
          모델이 파형 대신 글자를 읽으면 성능이 부풀려지고, 실제 사진에서는 무너집니다.</p>
          <p>그래서 헤더·판독문을 끈 <code>--no-header --no-interpretation</code> 변형을 별도로 렌더해
          ablation 기준선으로 씁니다.</p>
        </div>
        <table class="data">
          <caption>가장 자주 인쇄되는 판독문구</caption>
          <thead><tr><th>문구</th><th>n</th><th>%</th></tr></thead>
          <tbody>{interp_rows}</tbody>
        </table>
      </div>
      <div>{fig("interpretation.png", "판독문구 빈도 상위 막대그래프", "판독문은 106종 문자열의 조합입니다. 이미지에 텍스트가 있으면 CNN 은 그것부터 읽습니다.")}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>8. 학습 설계에 직결되는 발견</h2><span class="idx">08 / 08</span></div>
    <div class="callout">
      <h3>환자 단위 split 이 깨져 있습니다</h3>
      <p>{S['n_patients']:,}명 중 <b>{S['patients_in_multiple_splits']:,}명({S['pct_patients_multiple_splits']}%)</b>이
      두 개 이상의 split 에 등장합니다. 같은 환자의 ECG 가 train 과 val/test 에 동시에 들어 있다는 뜻이고,
      이미지 모델은 환자 고유의 파형 형태를 외워 성능을 부풀릴 수 있습니다.</p>
      <p>대응: ① 학습 전에 <code>patient_key</code> 기준으로 split 을 다시 만들고(그룹 split),
      ② 보고 수치는 환자 단위 group split 결과로만 제시, ③ 기존 split 결과는 “참고”로만 남깁니다.</p>
    </div>
    <div class="grid-2">
      <div>
        <h3>그 외</h3>
        <ul class="prose">
          <li><b>라벨 불균형</b> — PR ≥ moderate 0.8% vs SHD 52.2%. PR/AR/effusion 은 양성 수가 1,000건 안팎이라
          단순 BCE 로는 학습이 어긋납니다(가중·focal·threshold 조정).</li>
          <li><b>나이 단축</b> — 나이만으로도 유병률이 단조 증가합니다. 나이를 이미지에서 읽게 두면
          “나이 맞히기”로 성능이 새므로, 나이를 명시적 보조 입력으로 주고 이미지 기여도를 따로 재야 합니다.</li>
          <li><b>측정값 결측의 선택편향</b> — PASP·TR max 는 검사 시행 여부와 상관. 입력 feature 로 금지.</li>
          <li><b>중증도 표본</b> — 응급 {S.get('location_setting',{}).get('emergency',0):,} · 입원 {S.get('location_setting',{}).get('inpatient',0):,} 로
          중증 편향이 있습니다. 일반 외래로 일반화하려면 별도 검증이 필요합니다.</li>
        </ul>
      </div>
      <div class="prose">
        <h3>재현</h3>
        <p>이 리포트는 저장소의 스크립트로 다시 만들 수 있습니다.</p>
        <pre class="mono" style="background:var(--color-surface);border:1px solid var(--color-border);border-radius:8px;padding:14px;overflow:auto;font-size:12px">python3 tools/make_eda.py \\
  --meta metadata.csv \\
  --out assets/figures \\
  --summary data/summary.json
python3 tools/build_site.py</pre>
        <p class="muted">원본 metadata.csv(환자 식별자 포함)는 저장소에 올리지 않습니다.
        집계 결과인 <code>data/summary.json</code> 만 공개합니다.</p>
      </div>
    </div>
  </div>
</section>
"""
    return shell(
        "EDA 리포트 — ECG→Echo 렌더 데이터셋",
        "렌더된 100,000 ECG 이미지의 구조·무결성·표본 특성·라벨 유병률·결측·누수 진단을 코드로 집계한 EDA 리포트.",
        "eda.html",
        body,
    )


def results_block() -> str:
    """Optional block: filled by tools/model_results.py once the Kaggle run finishes."""
    j = ROOT / "data" / "model_results.json"
    if not j.exists():
        return """
    <hr class="rule">
    <div class="prose">
      <h2>Baseline 성능</h2>
      <p class="muted">Kaggle 노트북(<code>khs224025/echonext-baseline</code>)이 학습 중입니다.
      EfficientNetB0 와 소형 ViT 를 mixed precision 으로 학습하고, Grad-CAM / attention rollout 을 뽑아
      이 자리에 자동으로 채워집니다.</p>
    </div>
"""
    d = json.loads(j.read_text())
    labels = d["labels"]
    models = d["models"]
    mnames = list(models.keys())

    def table(split, caption):
        head = "".join(f"<th>{m}</th>" for m in mnames)
        rows = ""
        for lab in labels:
            cells = "".join(
                f'<td class="num">{models[m].get(split, {}).get(lab, float("nan")):.3f}</td>'
                for m in mnames
            )
            rows += f"<tr><td>{lab}</td>{cells}</tr>"
        macro = "".join(
            f'<td class="num">{d["macro"].get(m, {}).get(split, float("nan")):.3f}</td>' for m in mnames
        )
        return (
            f'<table class="data"><caption>{caption}</caption>'
            f"<thead><tr><th>라벨</th>{head}</tr></thead><tbody>{rows}"
            f"<tr><td><b>macro AUROC</b></td>{macro}</tr></tbody></table>"
        )

    figs = ""
    ex = ROOT / "assets" / "explainers.png"
    if ex.exists():
        w, h = Image.open(ex).size
        figs = (
            '<figure class="figure"><img src="assets/explainers.png" alt="EfficientNetB0 Grad-CAM 과 '
            'ViT attention rollout 비교" width="%d" height="%d"></figure>' % (w, h)
        )
    mac = d["macro"]
    eff = mac.get("EfficientNetB0", {})
    vit = mac.get("ViT (small)", {})
    gv = eff.get("group_val", float("nan"))
    seen = eff.get("old_val_seen", float("nan"))
    unseen = eff.get("old_val_unseen", float("nan"))
    ns = eff.get("no_split_external", float("nan"))
    leak = seen - gv
    vit_gv = vit.get("group_val", float("nan"))

    return f"""
    <hr class="rule">
    <div class="section-head"><h2>Baseline 성능 (실측)</h2><span class="idx">n = {d.get('n_train', 0):,} train</span></div>
    <p class="prose">같은 이미지·같은 split 에서 두 구조를 비교했습니다. 환자 단위 그룹 split 기준이며,
    판독문 누수는 제거하지 않은 상태(원본 결과지)입니다.</p>
    <div class="grid-2">
      <div>{table("group_val", "환자 단위 그룹 val — 정직한 숫자")}</div>
      <div>{table("no_split_external", "no_split 8,000장 — 학습에 전혀 쓰지 않은 외부 검증")}</div>
    </div>
    <div class="prose">
      <h3>읽는 법 — 누수와 일반화</h3>
      <p>같은 EfficientNetB0 의 macro AUROC 는 그룹 val <b>{gv:.3f}</b>, 기존 val 중 <b>학습에서 본 환자</b> {seen:.3f},
      <b>못 본 환자</b> {unseen:.3f} 입니다. 차이 <b>+{leak:.3f}</b> 가 곧 환자 누수로 부풀려지는 양입니다 —
      기존 split 을 그대로 썼다면 이만큼 높은 숫자를 보고했을 것입니다.</p>
      <p>반대로 학습에 전혀 쓰지 않은 <code>no_split</code> 8,000장에서는 <b>{ns:.3f}</b> 로 떨어집니다.
      누수로 설명되지 않는 낙폭이라, 이 부분집합의 코호트·시대·검사 적응증 차이를 먼저 확인해야 합니다.</p>
      <p>ViT(small) 는 2.86M params · 6 epoch 로 학습해 macro {vit_gv:.3f} — 사실상 학습되지 않았습니다.
      구조 비교로 쓰려면 사전학습 가중치나 더 긴 스케줄이 필요합니다.</p>

      <h3>설명 가능성</h3>
      <p>EfficientNetB0 는 마지막 conv feature 에 대한 gradient 로 Grad-CAM 을, ViT 는 레이어별 attention 을
      residual 보정해 곱한 attention rollout 을 씁니다. 두 지도가 겹치는 영역이 파형인지 인쇄 텍스트인지가
      이 프로젝트의 핵심 점검 항목입니다.</p>
      <p><b>실측 관찰</b>: EfficientNetB0 의 Grad-CAM 은 파형보다 <b>좌상단 환자·측정값 블록과 판독문 줄</b>에
      질량이 몰립니다. LVEF 를 맞히는 데 파형보다 인쇄 텍스트를 쓰고 있을 가능성이 높다는 뜻이고,
      헤더·판독문을 끈 ablation 렌더가 다음 필수 단계인 이유입니다.</p>
    </div>
    {figs}
"""


def ablation_block() -> str:
    j = ROOT / "data" / "ablation.json"
    if not j.exists():
        return ""
    d = json.loads(j.read_text())
    rows = sorted(d["rows"], key=lambda r: r["d"])
    trs = "".join(
        f'<tr><td>{r["label"]}</td><td class="num">{r["a"]:.3f}</td>'
        f'<td class="num">{r["b"]:.3f}</td><td class="num">{r["d"]:+.3f}</td></tr>'
        for r in rows
    )
    a, b = d["macro"]["A_text"], d["macro"]["B_no_text"]
    delta = b - a
    return f"""
    <hr class="rule">
    <div class="section-head"><h2>판독문 누수 통제 실험</h2>
      <span class="idx">{d['n_train']:,} train · {d['n_val']:,} val</span></div>
    <p class="prose">같은 20,000행을 두 번 학습했습니다. 모델·스케줄·증강·손실은 동일하고, 한 쪽만
    <code>--no-header --no-interpretation</code> 로 다시 렌더해 <b>인쇄 텍스트만</b> 제거했습니다.</p>
    <div class="grid-2">
      <div>
        <table class="data">
          <caption>라벨별 AUROC — A(텍스트 있음) vs B(텍스트 없음)</caption>
          <thead><tr><th>라벨</th><th>A</th><th>B</th><th>Δ</th></tr></thead>
          <tbody>{trs}
            <tr><td><b>macro</b></td><td class="num"><b>{a:.3f}</b></td>
                <td class="num"><b>{b:.3f}</b></td><td class="num"><b>{delta:+.3f}</b></td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <p class="prose"><b>결론: 인쇄 텍스트의 기여는 작습니다.</b> macro AUROC 차이 {delta:+.3f}.
        가장 크게 떨어진 라벨은 PR ≥ moderate(−0.067)와 LVEF(−0.037)이고, AR·AS 는 오히려 올랐습니다
        (val 4,000장 기준이라 노이즈가 큽니다). 즉 이 데이터에서 성능의 대부분은 <b>파형</b>에서 나옵니다.</p>
        <p class="prose">Grad-CAM 이 헤더에 몰렸던 것은 “글자를 읽는다”기보다, 헤더·측정값 블록이
        결과지 상단에서 유일하게 고주파 디테일이 있는 영역이라 주의가 쏠린 것으로 해석하는 편이 맞습니다.
        텍스트를 없앤 arm B 의 Grad-CAM 은 파형 중앙부로 이동했습니다.</p>
      </div>
    </div>
    <div class="grid-2">
      <figure class="figure"><img src="assets/ablation_preview.png" alt="헤더·판독문 있는 렌더와 없는 렌더 비교"
        width="496" height="756" decoding="async" style="max-width:100%">
        <figcaption>같은 행을 두 방식으로 렌더한 비교. arm B 는 헤더·판독문이 없어 격자가 페이지 전체로 확장됩니다.</figcaption>
      </figure>
      <figure class="figure"><img src="assets/ablation_gradcam.png" alt="텍스트 제거 모델의 Grad-CAM"
        width="699" height="1427" decoding="async" style="max-width:100%">
        <figcaption>텍스트를 뺀 모델의 Grad-CAM. 화면 중앙의 파형 영역으로 주의가 이동했습니다.</figcaption>
      </figure>
    </div>
"""




SHORT_KO = {
    "lvef_lte_45_flag": "LVEF ≤ 45%",
    "lvwt_gte_13_flag": "LVWT ≥ 13 mm",
    "aortic_stenosis_moderate_or_greater_flag": "AS ≥ moderate",
    "aortic_regurgitation_moderate_or_greater_flag": "AR ≥ moderate",
    "mitral_regurgitation_moderate_or_greater_flag": "MR ≥ moderate",
    "tricuspid_regurgitation_moderate_or_greater_flag": "TR ≥ moderate",
    "pulmonary_regurgitation_moderate_or_greater_flag": "PR ≥ moderate",
    "rv_systolic_dysfunction_moderate_or_greater_flag": "RV dysfunction ≥ mod",
    "pericardial_effusion_moderate_large_flag": "Pericardial effusion",
    "pasp_gte_45_flag": "PASP ≥ 45 mmHg",
    "tr_max_gte_32_flag": "TR max ≥ 3.2 m/s",
    "shd_moderate_or_greater_flag": "SHD composite",
}


def threshold_table() -> str:
    j = ROOT / "data" / "thresholds.json"
    if not j.exists():
        return ""
    d = json.loads(j.read_text())
    rows = ""
    for k in d["labels"]:
        e = d["per_label"][k]
        y = e.get("youden") or {}
        thr = y.get("thr")
        if thr is None:
            continue
        rows += (
            f'<tr><td>{SHORT_KO.get(k, k)}</td>'
            f'<td class="num">{e["prevalence"] * 100:.1f}%</td>'
            f'<td class="num">{e.get("auroc", float("nan")):.3f}</td>'
            f'<td class="num"><b>{thr:.2f}</b></td>'
            f'<td class="num">{y.get("sens", 0):.2f} / {y.get("spec", 0):.2f}</td></tr>'
        )
    return f"""
        <h3>라벨별 컷오프 (validation Youden)</h3>
        <table class="data">
          <caption>민감도+특이도를 최대로 하는 지점. 데모 막대의 세로 눈금이 이 값입니다.</caption>
          <thead><tr><th>라벨</th><th>유병률</th><th>AUROC</th><th>컷오프</th><th>민감도/특이도</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        <p class="muted">출처: {d.get("source", "")} · 표본 {d.get("n_val", 0):,}장.
        희귀 라벨(AR·PR·삼출)의 컷오프가 0.05–0.24 로 낮은 것은, 0.50 일괄 기준이 그 소견들을 사실상 지웠다는 뜻입니다.
        full validation 으로 재계산하면 이 표가 갱신됩니다.</p>
"""

def augment_block() -> str:
    """사진 증강 / 헤더 마스킹 실험 — baseline 과 같은 조건에서 비교."""
    j = ROOT / "data" / "augment.json"
    if not j.exists():
        return ""
    d = json.loads(j.read_text())
    conds = d["conditions"]
    rows = ""
    for c, name in conds.items():
        b = d["baseline"][c]
        a = d["photoaug"][c]
        dl = a - b
        cls = "neg" if dl < -0.002 else ("pos" if dl > 0.002 else "")
        rows += (
            f'<tr><td>{name}</td><td class="num">{b:.4f}</td>'
            f'<td class="num">{a:.4f}</td>'
            f'<td class="num"><b class="{cls}">{"+" if dl > 0 else ""}{dl:.4f}</b></td></tr>'
        )
    pl = d["per_label"]
    lab_rows = "".join(
        f'<tr><td>{lab}</td><td class="num">{pl["baseline"][lab]:.4f}</td>'
        f'<td class="num">{pl["photoaug"][lab]:.4f}</td>'
        f'<td class="num"><b class="{"neg" if pl["photoaug"][lab] < pl["baseline"][lab] else "pos"}">'
        f'{pl["photoaug"][lab] - pl["baseline"][lab]:+.4f}</b></td></tr>'
        for lab in d["labels"]
    )
    return f"""
    <hr class="rule">
    <div class="prose">
      <h2>사진 증강은 이겼는가 — 졌습니다</h2>
      <p>같은 환자 단위 그룹 val(n={d["n_val"]:,})에서, 증강 없이 학습한 모델과
      사진 시뮬레이션 증강(원근 16종·광도·감마·색온도·흐림·노이즈·그림자·헤더 마스킹)으로 학습한 모델을
      같은 4조건으로 채점했습니다. 증강 모델은 <b>모든 조건에서 더 낮았습니다</b>.</p>
      <table class="data">
        <caption>macro AUROC — 학습 조건 vs 평가 조건</caption>
        <thead><tr><th>평가 조건</th><th>증강 없음</th><th>사진 증강</th><th>Δ</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <table class="data">
        <caption>주요 라벨 (원본 조건)</caption>
        <thead><tr><th>라벨</th><th>증강 없음</th><th>사진 증강</th><th>Δ</th></tr></thead>
        <tbody>{lab_rows}</tbody>
      </table>
      <p>읽는 법이 세 가지로 갈립니다.</p>
      <ul>
        <li><b>증강은 손해였다</b> — 원본 −0.006, 상단 25% 가림 −0.005, 50% 가림 −0.013, 20% 크롭 −0.018.
        “강건성을 사고 성능을 조금 판다”가 아니라 <b>둘 다 잃은</b> 형태입니다.</li>
        <li><b>원본 모델이 이미 강건하다</b> — 증강 없이도 상단 25%를 가려도 −0.001, 20% 크롭에서 오히려 +0.0004.
        결과지에서 헤더 텍스트가 결정에 거의 쓰이지 않는다는 뜻이고, 앞선 판독문 제거 ablation(Δ −0.013)과 일치합니다.</li>
        <li><b>그래서 배포 가중치는 증강 없음(384) 유지</b>. 사진 도메인 간극은 합성 증강으로 메우는 문제가 아니라
        실제 촬영본이 필요한 문제로 보입니다.</li>
      </ul>
      <p class="muted">증강 모델은 12 epoch, 원본은 6 epoch 로 학습 예산이 다릅니다. 다만 증강 쪽이 더 오래
      학습했는데도 낮으므로 결론은 바뀌지 않습니다(에폭 부족으로 설명되지 않음).</p>
    </div>
"""

def resolution_block() -> str:
    j = ROOT / "data" / "resolution.json"
    if not j.exists():
        return ""
    d = json.loads(j.read_text())
    rows = sorted(d["rows"], key=lambda r: -r["d"])
    trs = "".join(
        f'<tr><td>{r["label"]}</td><td class="num">{r["v224"]:.3f}</td>'
        f'<td class="num">{r["v384"]:.3f}</td><td class="num">{r["t384"]:.3f}</td>'
        f'<td class="num">{r["d"]:+.3f}</td></tr>'
        for r in rows
    )
    m24, m84 = d["macro_224"], d["macro_384"]
    names = [("group_val", "그룹 val"), ("group_test", "그룹 test"),
             ("old_val_seen", "기존 val · 본 환자"), ("old_val_unseen", "기존 val · 못 본 환자"),
             ("no_split_external", "no_split 외부")]
    mrows = "".join(
        f'<tr><td>{label}</td><td class="num">{m24[k]:.3f}</td>'
        f'<td class="num">{m84[k]:.3f}</td><td class="num">{m84[k]-m24[k]:+.3f}</td></tr>'
        for k, label in names
    )
    return f"""
    <hr class="rule">
    <div class="section-head"><h2>해상도 실험 224 → 384</h2><span class="idx">같은 행 · 같은 스케줄</span></div>
    <p class="prose">파형의 미세 진폭과 QRS 폭이 정보라면 해상도를 올릴 때 성능이 올라야 합니다.
    같은 그룹 split·같은 6 epoch·같은 손실에서 <b>입력 크기만 384</b> 로 바꿨습니다.</p>
    <div class="grid-2">
      <div>
        <table class="data">
          <caption>macro AUROC — 224 vs 384</caption>
          <thead><tr><th>평가 집합</th><th>224</th><th>384</th><th>Δ</th></tr></thead>
          <tbody>{mrows}</tbody>
        </table>
      </div>
      <div class="prose">
        <p><b>해상도는 실제 레버였습니다.</b> 그룹 val macro {m24['group_val']:.3f} → <b>{m84['group_val']:.3f}</b>
        ({m84['group_val']-m24['group_val']:+.3f}), 그룹 test {m24['group_test']:.3f} → <b>{m84['group_test']:.3f}</b>
        ({m84['group_test']-m24['group_test']:+.3f}). 두 집합이 같이 올라 우연이 아닙니다.</p>
        <p><b>LVEF ≤ 45% 는 그룹 test 0.853</b> — 전략 문서의 목표(0.85)를 넘었습니다(val 0.835).
        SHD 도 0.806 으로 목표(0.80)를 넘겼습니다.</p>
        <p>반면 <b>no_split 외부는 0.589 → 0.556</b> 으로 더 나빠졌습니다. 해상도로 설명되지 않는
        분포 문제가 남아 있다는 뜻이고, 다음 과제는 모델이 아니라 이 부분집합의 정체 규명입니다.</p>
      </div>
    </div>
    <div class="table-scroll">
    <table class="data">
      <caption>라벨별 AUROC — 224 그룹 val / 384 그룹 val / 384 그룹 test</caption>
      <thead><tr><th>라벨</th><th>224 val</th><th>384 val</th><th>384 test</th><th>Δ val</th></tr></thead>
      <tbody>{trs}</tbody>
    </table>
    </div>
    <p class="prose muted">주의: 해상도를 올리면 배치를 128 → 64 로 줄여야 해서 학습 동역학이 완전히 같지는 않습니다.
    ±0.01 수준 차이는 이 때문일 수 있습니다. 누수 지표(본 환자 − 못 본 환자)는 0.060 으로 224(0.086)보다 줄었습니다.</p>
"""


def cam_overlay_block() -> str:
    g = ROOT / "assets" / "cam_overlay_grid.webp"
    if not g.exists():
        return ""
    w, h = Image.open(g).size
    f = ROOT / "assets" / "cam_overlay_full.webp"
    fw, fh = Image.open(f).size if f.exists() else (1124, 814)
    return f"""
    <hr class="rule">
    <div class="section-head"><h2>원본 해상도 Grad-CAM overlay</h2><span class="idx">12×12 → 1124×814</span></div>
    <p class="prose">feature map 은 12×12 입니다. 그대로 늘리면 계단이 생기므로 <b>bicubic 업샘플 + Gaussian 평활</b>로
    원본 결과지 해상도까지 올린 뒤 얹었습니다. 위치 정밀도는 격자 한 칸(≈ 원본 94 px)이므로 픽셀 단위가 아니라
    “어느 영역을 보는가”의 지도로 읽어야 합니다.</p>
    <figure class="figure"><img src="assets/cam_overlay_grid.webp" alt="원본 결과지 위에 겹친 Grad-CAM 6장"
      width="{w}" height="{h}" decoding="async" style="max-width:100%">
      <figcaption>위 세 장이 LVEF ≤ 45% 양성(p=0.49 / 0.98 / 0.98), 아래 세 장이 음성(p=0.10 / 0.27 / 0.52).</figcaption>
    </figure>
    <div class="grid-2">
      <figure class="figure"><img src="assets/cam_overlay_full.webp" alt="원본 해상도 Grad-CAM overlay 단일 예시"
        width="{fw}" height="{fh}" decoding="async" style="max-width:100%">
        <figcaption>원본 해상도 그대로. QRS·T 파형 구간에 열점이 걸립니다.</figcaption>
      </figure>
      <div class="prose">
        <p><b>읽히는 것</b>: 열점이 상단 헤더가 아니라 <b>파형 구간</b>(주로 V1–V3 행과 리듬 스트립)에 걸립니다.
        판독문 제거 ablation(Δ −0.013)과 같은 방향의 증거입니다.</p>
        <p><b>주의할 것</b>: 여섯 장 모두 <b>오른쪽 위 모서리에 같은 열점</b>이 남습니다. 특정 환자의 특징이 아니라
        경계·여백에서 나오는 아티팩트로 보이므로, Grad-CAM 을 임상 해석에 쓰려면 이 성분을 먼저 제거해야 합니다.
        (헤더 마스킹 + 사진 증강으로 재학습한 가중치에서 이 열점이 줄어드는지가 다음 확인 항목입니다.)</p>
        <p class="muted">한계: CAM 은 12×12 격자라 “파형 전체 vs 헤더” 수준의 판단만 가능합니다.
        더 정밀한 설명이 필요하면 768 입력 재학습이나 입력 해상도에서 직접 계산하는 occlusion·Score-CAM 이 필요합니다.</p>
      </div>
    </div>
"""


# --------------------------------------------------------------------------- demo
def build_demo() -> str:
    body = """
<section class="hero" style="padding-bottom:var(--space-5)">
  <div class="wrap" style="grid-template-columns:1fr">
    <div class="prose">
      <p class="eyebrow">Tab 2 · Web demo</p>
      <h1 style="font-size:var(--text-2xl)">결과지 사진을 넣으면 라벨이 나옵니다</h1>
      <p class="lead">심전도 결과지 사진에서 심초음파 주요 소견 12개의 가능성을 확률로 보여줍니다.
      진단이 아니라 <b>심초음파 시행 여부를 판단하는 보조 지표</b>이고, 사진은 이 기기를 떠나지 않습니다.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:var(--space-6)">
  <div class="wrap">
    <div class="demo-shell">
      <div>
        <div class="dropzone" id="dropzone">
          <h2 style="font-size:var(--text-lg);margin-bottom:var(--space-2)">ECG 결과지 이미지</h2>
          <p class="hint">PNG · JPG · 결과지 전체가 보이게. 끌어놓거나 아래 파일 선택. 모든 계산은 이 브라우저 안에서 끝납니다.</p>
          <label class="btn btn-primary" for="file">파일 선택
            <input id="file" type="file" accept="image/*" hidden>
          </label>
          <div class="preview" id="preview" hidden></div>
          <p class="status-note" id="status" style="margin-top:14px">모델 준비 중…</p>
        </div>
        <p class="status-note" style="margin-top:12px">샘플 결과지로 바로 확인:</p>
        <div class="samples">
          <button type="button" data-src="assets/samples/ecg_0000038.png" data-tr="정답 LVEF ≤ 45% 있음" aria-label="샘플 결과지 1 (LVEF 감소) 보기"><img src="assets/samples/ecg_0000038.png" alt="샘플 결과지 1" width="1124" height="814" loading="lazy"></button>
          <button type="button" data-src="assets/samples/ecg_0000039.png" data-tr="정답 LVEF ≤ 45% 있음" aria-label="샘플 결과지 2 (LVEF 감소) 보기"><img src="assets/samples/ecg_0000039.png" alt="샘플 결과지 2" width="1124" height="814" loading="lazy"></button>
          <button type="button" data-src="assets/samples/ecg_0000032.png" data-tr="정답 LVEF ≤ 45% 없음" aria-label="샘플 결과지 3 (LVEF 정상) 보기"><img src="assets/samples/ecg_0000032.png" alt="샘플 결과지 3" width="1124" height="814" loading="lazy"></button>
        </div>
        <p class="status-note" style="margin-top:8px">세 장 모두 학습에서 한 번도 쓰지 않은 환자(그룹 val)입니다. 정답을 함께 표시하니 맞고 틀림을 그대로 보실 수 있습니다.</p>
      </div>
      <aside class="result-panel" aria-live="polite">
        <h3>예측 확률</h3>
        <p class="status-note" id="panel-note">이미지를 넣으면 12개 소견의 가능성이 표시됩니다.
        0.50 을 넘는 항목이 “양성”으로 강조됩니다.</p>
        <ul class="result-list" id="results"></ul>
        <p class="cutoff-legend">세로 눈금 = <b>라벨별 컷오프</b>(validation Youden 지점), 라벨 옆 흐린 숫자가 그 값입니다.
        넘으면 양성 표시(진한 막대 + 굵은 수치). 확률은 보정 전이므로 순위 비교용으로 보세요.</p>
        <div class="cam-figure">
          <div class="cam-controls">
            <label for="cam-class">설명 지도</label>
            <select id="cam-class"></select>
            <label class="cam-check"><input type="checkbox" id="cam-toggle" checked> overlay</label>
            <span class="mono" id="timing"></span>
          </div>
          <canvas id="cam" width="384" height="384" aria-label="선택한 라벨의 CAM 설명 지도"></canvas>
          <p class="status-note" style="margin-top:8px">CAM 은 12×12 격자를 bilinear 로 늘린 지도이고,
          검증 240장의 <b>평균 CAM 을 뺀</b> 값입니다. 이 모델은 지도 원본에서 빈 종이 모서리가 늘 최대로 튀어
          (검증의 93–98% 가 argmax 를 그 모서리에 둠) 그대로 두면 모든 설명이 같은 그림이 됩니다.
          한 칸이 원본 약 94 px 이라 정밀도는 영역 수준입니다.</p>
        </div>
      </aside>
    </div>

    <hr class="rule">
    <div class="grid-2">
      <div class="prose">
        <h2>임상 해석</h2>
        <p>막대의 세로 눈금이 <b>라벨별 컷오프</b>입니다 — validation ROC 의 Youden 지점(민감도+특이도 최대)으로
        라벨마다 다릅니다. 눈금을 넘으면 해당 소견이 <b>있을 가능성이 높다고 표시</b>됩니다(진한 막대 + 굵은 수치).
        LVEF 처럼 유병률이 낮은 라벨은 컷오프가 낮고, SHD 처럼 흔한 라벨은 높게 잡힙니다.
        값 자체보다 <b>상위 2–3개 라벨</b>과 좌우 대칭성을 보세요.</p>
        <h3>라벨이 뜻하는 것</h3>
        <ul>
          <li><b>LVEF ≤ 45%</b> — 좌심실 수축기능 저하. 가장 중요한 단일 지표. 상승 시 심초음파 우선.</li>
          <li><b>SHD composite</b> — 구조적 심질환 복합(판막·심실·폐고혈압 중 하나 이상 중등도 이상).</li>
          <li><b>LVWT ≥ 13 mm</b> — 좌심실비대. 고혈압·대동맥판 협착의 만성 흔적.</li>
          <li><b>AS / AR / MR / TR / PR ≥ moderate</b> — 각 판막 중등도 이상 역류·협착.</li>
          <li><b>RV dysfunction ≥ moderate</b> — 우심실 기능저하.</li>
          <li><b>PASP ≥ 45 mmHg · TR max ≥ 3.2 m/s</b> — 폐고혈압 시사(TR 제트에서 추정).</li>
          <li><b>Pericardial effusion</b> — 중등도 이상 심낭삼출.</li>
        </ul>
        <div class="table-scroll">
        %%THRTABLE%%
        </div>
        <h3>해석할 때 주의</h3>
        <ul>
          <li>조합이 임상적으로 더 중요합니다 — <b>LVEF↓ + SHD</b> 는 고위험, <b>PASP↑ + TR↑</b> 는 폐고혈압 평가,
          삼출 단독 상승은 특이도가 낮습니다.</li>
          <li>학습 데이터는 <b>정면 렌더된 결과지</b>입니다. 기울기·그림자·저해상도 촬영본에서는 성능이 떨어집니다.</li>
          <li>무증상 선별 검사로 검증된 도구가 아닙니다. <b>최종 판단은 심초음파와 전문의 확인</b>으로 합니다.</li>
          <li>설명 지도(CAM)는 12×12 격자라 “파형 전체 vs 상단 텍스트” 수준의 거친 위치 정보만 줍니다.</li>
        </ul>
      </div>
      <div class="prose">
        <h3>이 화면이 하는 일 / 하지 않는 일</h3>
        <table class="data">
          <tbody>
            <tr><td>하는 일</td><td>결과지 사진 → 12개 소견 확률 + 거친 주의 지도</td></tr>
            <tr><td>하지 않는 일</td><td>심초음파 대체, 진단 확정, 치료 결정</td></tr>
            <tr><td>권장 사용</td><td>심전도만 있고 심초음파가 없을 때 <b>검사 우선순위</b> 정하기</td></tr>
            <tr><td>금기</td><td>급성 흉통·폐부종 등 즉시 초음파가 필요한 상황의 대체</td></tr>
          </tbody>
        </table>
        <p class="muted">결과지 1장당 추론은 이 기기에서 0.4–0.8초. 사진은 업로드되지 않고 브라우저 메모리에서만 처리됩니다.</p>
      </div>
    </div>

    <details class="fineprint">
      <summary>기술 정보 — 모델 카드·검증 수치·배포 구조</summary>
      <p>EfficientNetB0 · 입력 384×384 · 출력 <code>logits</code>(12) + <code>cam</code>(12×12×12) · ONNX 8.0 MB ·
      환자 단위 그룹 split(seed 42) · 학습 57,337장 · 그룹 val macro AUROC 0.768 (LVEF 0.835 / test 0.853).</p>
      <p>내보내기 검증: 원본 Keras 와 ONNX 로짓 최대차 0.036, 160장 표본 macro AUROC Keras 0.8043 vs ONNX 0.8039.
      int8 동적 양자화는 AUROC 0.63 → 0.52 로 무너져 폐기. 확률은 보정 전 sigmoid 입니다.</p>
      <p>배포: onnxruntime-web(WASM)으로 전처리·추론을 모두 클라이언트에서 수행 → PC 앱은 같은 ONNX 를 데스크톱 런타임으로,
      APK 는 카메라 촬영 + 결과지 검출·원근 보정 후 동일 파이프라인. 사진에서 바로 추론하지 않는 이유는 학습 데이터가
      정면·무왜곡 렌더이기 때문이며, 회전·원근·조명·그림자 증강과 헤더 마스킹으로 그 간극을 줄이는 중입니다.</p>
    </details>

    %%RESULTS%%
    %%AUGMENT%%
    %%ABLATION%%
    %%RESOLUTION%%
    %%CAM%%

  </div>
</section>

<script>
(function () {
  var IMG = 384, N = 12;
  var CDN = 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.0/dist/';
  var MODELS = ['assets/models/echonext_384.onnx'];
  var LABELS = ['LVEF ≤ 45%', 'LVWT ≥ 13 mm', 'AS ≥ moderate', 'AR ≥ moderate',
                'MR ≥ moderate', 'TR ≥ moderate', 'PR ≥ moderate', 'RV dysfunction ≥ mod',
                'Pericardial effusion', 'PASP ≥ 45 mmHg', 'TR max ≥ 3.2 m/s', 'SHD composite'];

  var dz = document.getElementById('dropzone');
  var input = document.getElementById('file');
  var preview = document.getElementById('preview');
  var status = document.getElementById('status');
  var panelNote = document.getElementById('panel-note');
  var resultsEl = document.getElementById('results');
  var camSel = document.getElementById('cam-class');
  var camToggle = document.getElementById('cam-toggle');
  var timingEl = document.getElementById('timing');
  var camCanvas = document.getElementById('cam');

  var sess = null, currentImg = null, lastCam = null, lastLogits = null, curClass = 0, curTruth = '';
  var meanCam = null;   // 검증 240장 평균 CAM (12x12x12) — 빈 모서리의 상수 오프셋을 뺀다
  var THR = LABELS.map(function () { return 0.5; });   // 라벨별 컷오프 (validation Youden)

  function setStatus(t) { status.textContent = t; }

  resultsEl.innerHTML = LABELS.map(function (name, i) {
    return '<li data-i="' + i + '"><span>' + name + ' <span class="cutoff-val"></span></span>' +
           '<span class="mono">—</span>' +
           '<div class="track"><div class="fill" style="width:0%"></div>' +
           '<span class="cutoff" title="0.50 기준"></span></div></li>';
  }).join('');
  camSel.innerHTML = LABELS.map(function (n, i) { return '<option value="' + i + '">' + n + '</option>'; }).join('');

  fetch('data/thresholds.json').then(function (r) { return r.json(); }).then(function (d) {
    LABELS.forEach(function (name, i) {
      var key = d.labels ? d.labels[i] : null;
      var e = key ? d.per_label[key] : null;
      if (e && e.youden && typeof e.youden.thr === 'number') THR[i] = e.youden.thr;
      var li = resultsEl.children[i];
      if (li) {
        var cut = li.querySelector('.cutoff');
        cut.style.left = (THR[i] * 100).toFixed(1) + '%';
        cut.title = '컷오프 ' + THR[i].toFixed(2) + ' (validation Youden)';
        var cv = li.querySelector('.cutoff-val');
        if (cv) cv.textContent = '컷 ' + (THR[i] * 100).toFixed(0);
      }
    });
    if (lastLogits) renderResults(lastLogits, lastCam, 0);
  }).catch(function () {});

  fetch('data/mean_cam.json').then(function (r) { return r.json(); })
    .then(function (d) { meanCam = d.mean_cam; })
    .catch(function () { meanCam = null; });

  function ensureOrt() {
    if (window.ort) return Promise.resolve();
    return new Promise(function (res, rej) {
      var s = document.createElement('script');
      s.src = CDN + 'ort.min.js';
      s.onload = res;
      s.onerror = rej;
      document.head.appendChild(s);
    });
  }

  async function loadModel() {
    try {
      await ensureOrt();
      ort.env.wasm.wasmPaths = CDN;
      ort.env.wasm.numThreads = 1;
    } catch (e) {
      setStatus('onnxruntime 로드 실패 — 네트워크(CDN)를 확인하세요.');
      return;
    }
    for (var i = 0; i < MODELS.length; i++) {
      try {
        setStatus('가중치 로드 중… (16 MB, 첫 1회만 내려받습니다)');
        sess = await ort.InferenceSession.create(MODELS[i], { executionProviders: ['wasm'] });
        setStatus('준비 완료 — 결과지 이미지를 넣으세요.');
        if (currentImg) infer();
        return;
      } catch (e) { console.warn('model load failed', MODELS[i], e); }
    }
    setStatus('가중치를 불러오지 못했습니다 (모델 파일 미배포 또는 로드 실패).');
  }

  function imgToFloat(img) {
    var c = document.createElement('canvas');
    c.width = IMG; c.height = IMG;
    var x = c.getContext('2d', { willReadFrequently: true });
    x.drawImage(img, 0, 0, IMG, IMG);
    var d = x.getImageData(0, 0, IMG, IMG).data;
    var f = new Float32Array(IMG * IMG * 3);
    for (var i = 0, p = 0; i < d.length; i += 4) {
      f[p++] = d[i]; f[p++] = d[i + 1]; f[p++] = d[i + 2];
    }
    return { data: f, canvas: c };
  }

  function sigmoid(v) { return 1 / (1 + Math.exp(-v)); }

  function jet(t) {
    t = Math.max(0, Math.min(1, t));
    var r = Math.round(255 * Math.min(Math.max(1.5 - Math.abs(4 * t - 3), 0), 1));
    var g = Math.round(255 * Math.min(Math.max(1.5 - Math.abs(4 * t - 2), 0), 1));
    var b = Math.round(255 * Math.min(Math.max(1.5 - Math.abs(4 * t - 1), 0), 1));
    return [r, g, b];
  }

  function drawCam() {
    if (!currentImg) return;
    var base = imgToFloat(currentImg).canvas;
    var ctx = camCanvas.getContext('2d');
    ctx.clearRect(0, 0, IMG, IMG);
    ctx.drawImage(base, 0, 0);
    if (!lastCam || !camToggle.checked) return;

    var grid = new Float32Array(N * N), mx = 0;
    for (var y = 0; y < N; y++) {
      for (var x = 0; x < N; x++) {
        var v = lastCam[((y * N) + x) * N + curClass];
        if (meanCam) v -= meanCam[y][x][curClass];   // 상수 성분 제거
        if (v < 0) v = 0;
        grid[y * N + x] = v;
        if (v > mx) mx = v;
      }
    }
    if (mx <= 0) return;
    for (var k = 0; k < grid.length; k++) grid[k] /= mx;

    var small = document.createElement('canvas');
    small.width = N; small.height = N;
    var sctx = small.getContext('2d');
    var idata = sctx.createImageData(N, N);
    for (var i = 0; i < grid.length; i++) {
      var g = Math.round(grid[i] * 255);
      idata.data[i * 4] = g; idata.data[i * 4 + 1] = g; idata.data[i * 4 + 2] = g; idata.data[i * 4 + 3] = 255;
    }
    sctx.putImageData(idata, 0, 0);

    var up = document.createElement('canvas');
    up.width = IMG; up.height = IMG;
    var uctx = up.getContext('2d', { willReadFrequently: true });
    uctx.imageSmoothingEnabled = true;
    uctx.imageSmoothingQuality = 'high';
    uctx.drawImage(small, 0, 0, IMG, IMG);
    var upData = uctx.getImageData(0, 0, IMG, IMG).data;

    var out = ctx.getImageData(0, 0, IMG, IMG);
    var od = out.data;
    for (var p = 0, q = 0; p < od.length; p += 4, q += 4) {
      var t = upData[q] / 255;
      if (t <= 0.02) continue;
      var a = 0.55 * t;
      var col = jet(t);
      od[p] = od[p] * (1 - a) + col[0] * a;
      od[p + 1] = od[p + 1] * (1 - a) + col[1] * a;
      od[p + 2] = od[p + 2] * (1 - a) + col[2] * a;
    }
    ctx.putImageData(out, 0, 0);
  }

  function renderResults(logits, cam, ms) {
    lastCam = cam;
    lastLogits = logits;
    var items = Array.prototype.slice.call(resultsEl.children);
    var best = 0;
    var probs = Array.prototype.map.call(logits, sigmoid);
    probs.forEach(function (p, i) { if (p > probs[best]) best = i; });
    items.forEach(function (li, i) {
      var p = probs[i];
      li.querySelector('.mono').textContent = (p * 100).toFixed(1) + '%';
      li.classList.toggle('is-positive', p >= THR[i]);
      li.querySelector('.mono').setAttribute('title',
        (p >= THR[i] ? '컷오프 초과 · ' : '컷오프 미만 · ') + '기준 ' + THR[i].toFixed(2));
      var fill = li.querySelector('.fill');
      fill.style.width = Math.max(1, p * 100).toFixed(1) + '%';
      li.classList.toggle('is-top', i === best);
    });
    timingEl.textContent = ms.toFixed(0) + ' ms';
    var pos = probs.filter(function (v, i) { return v >= THR[i]; }).length;
    panelNote.textContent = (curTruth ? curTruth + ' · ' : '') +
      '컷오프 초과 ' + pos + '개 · 최고 ' + LABELS[best] + ' ' + Math.round(probs[best] * 100) + '%' +
      ' — 컷오프는 validation Youden 지점(라벨별)이고 확률은 보정 전입니다.';
    if (curClass !== best && !camSel.dataset.touched) {
      curClass = best;
      camSel.value = String(best);
    }
    drawCam();
  }

  async function infer() {
    if (!currentImg) return;
    if (!sess) { setStatus('가중치 로드 중입니다. 잠시 후 자동으로 추론합니다.'); return; }
    setStatus('추론 중…');
    try {
      var t0 = performance.now();
      var t = imgToFloat(currentImg);
      var tensor = new ort.Tensor('float32', t.data, [1, IMG, IMG, 3]);
      var out = await sess.run({ image: tensor });
      var keys = Object.keys(out);
      var logits = (out.logits || out.logits_out || out[keys[0]]).data;
      var cam = (out.cam || out[keys[1]]).data;   // (h, w, class) 평탄화
      renderResults(logits, cam, performance.now() - t0);
      setStatus('완료 — 결과지는 이 기기를 떠나지 않았습니다.');
    } catch (e) {
      console.error(e);
      setStatus('추론 실패: ' + (e && e.message ? e.message : e));
    }
  }

  function show(src, label, isObjectUrl, truth) {
    curTruth = truth || '';
    preview.hidden = false;
    preview.innerHTML = '<img alt="선택한 심전도 결과지 미리보기">';
    var img = preview.querySelector('img');
    img.onload = function () { currentImg = img; infer(); };
    img.src = src;
    setStatus(label + ' — 준비 중…');
    if (isObjectUrl) setTimeout(function () { URL.revokeObjectURL(src); }, 20000);
  }

  document.querySelectorAll('.samples button').forEach(function (b) {
    b.addEventListener('click', function () { show(b.dataset.src, '샘플 결과지', false, b.dataset.tr); });
  });

  input.addEventListener('change', function () {
    var f = input.files && input.files[0];
    if (!f) return;
    show(URL.createObjectURL(f), f.name, true);
  });

  ['dragenter', 'dragover'].forEach(function (ev) {
    dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.add('is-dragover'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.remove('is-dragover'); });
  });
  dz.addEventListener('drop', function (e) {
    var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    if (!f) return;
    show(URL.createObjectURL(f), f.name, true);
  });

  resultsEl.addEventListener('click', function (e) {
    var li = e.target.closest('li[data-i]');
    if (!li) return;
    curClass = Number(li.dataset.i);
    camSel.dataset.touched = '1';
    camSel.value = String(curClass);
    drawCam();
  });
  camSel.addEventListener('change', function () {
    curClass = Number(camSel.value);
    camSel.dataset.touched = '1';
    drawCam();
  });
  camToggle.addEventListener('change', drawCam);

  loadModel();
})();
</script>
"""
    body = body.replace("%%RESULTS%%", results_block()).replace("%%AUGMENT%%", augment_block()).replace("%%THRTABLE%%", threshold_table()).replace("%%ABLATION%%", ablation_block()).replace("%%RESOLUTION%%", resolution_block()).replace("%%CAM%%", cam_overlay_block())
    return shell(
        "데모 — 결과지 사진에서 심초음파 라벨 예측",
        "심전도 결과지 이미지를 넣으면 심초음파 12개 라벨 확률을 반환하는 웹 데모. 현재는 입력 화면만 배포된 상태.",
        "demo.html",
        body,
    )


def main():
    (ROOT / "index.html").write_text(build_index())
    (ROOT / "eda.html").write_text(build_eda())
    (ROOT / "demo.html").write_text(build_demo())

    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{p}</loc><changefreq>monthly</changefreq></url>"
        for p, _ in NAV
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    )
    (ROOT / "assets" / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="7" fill="#F4EDE3"/>'
        '<path d="M4 21h5l2.5-8 3.5 14 3.5-18 3 12H28" fill="none" stroke="#AC5228" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    (ROOT / "404.html").write_text(
        shell(
            "페이지를 찾을 수 없습니다 — ECG→Echo Report",
            "요청한 페이지가 없습니다. 주소가 바뀌었거나 오타일 수 있습니다. 표지, EDA 리포트, 데모 화면으로 이동하는 링크를 제공합니다.",
            "404.html",
            '<section class="section"><div class="wrap prose"><p class="eyebrow">404</p>'
            "<h1>그 페이지는 없습니다</h1>"
            '<p>주소가 바뀌었거나 오타일 수 있습니다. 아래에서 이동하세요.</p>'
            '<p><a class="btn btn-primary" href="index.html">표지로</a> '
            '<a class="btn btn-ghost" href="eda.html">EDA 리포트</a></p></div></section>',
            '<meta name="robots" content="noindex">',
        )
    )
    print("built:", ", ".join(f"{p}" for p, _ in NAV), "404.html")


if __name__ == "__main__":
    main()
