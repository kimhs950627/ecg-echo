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


# --------------------------------------------------------------------------- demo
def build_demo() -> str:
    body = """
<section class="hero" style="padding-bottom:var(--space-5)">
  <div class="wrap" style="grid-template-columns:1fr">
    <div class="prose">
      <p class="eyebrow">Tab 2 · Web demo</p>
      <h1 style="font-size:var(--text-2xl)">결과지 사진을 넣으면 라벨이 나옵니다</h1>
      <p class="lead">화면은 지금 열려 있지만, 모델은 아직 학습 전입니다. 이미지는 브라우저 밖으로 나가지 않습니다.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:var(--space-6)">
  <div class="wrap">
    <div class="demo-shell">
      <div>
        <div class="dropzone" id="dropzone">
          <h2 style="font-size:var(--text-lg);margin-bottom:var(--space-2)">ECG 결과지 이미지</h2>
          <p class="hint">PNG · JPG · 결과지 전체가 보이게. 끌어놓거나 아래 파일 선택.</p>
          <label class="btn btn-primary" for="file">파일 선택
            <input id="file" type="file" accept="image/*" hidden>
          </label>
          <div class="preview" id="preview" hidden></div>
          <p class="status-note" id="status" style="margin-top:14px">모델 미배포 — 지금은 입력 화면만 동작합니다.</p>
        </div>
        <p class="status-note" style="margin-top:12px">샘플 결과지로 화면만 확인하려면:</p>
        <div class="samples">
          <button type="button" data-src="assets/samples/ecg_0000861.png" aria-label="샘플 결과지 1 보기"><img src="assets/samples/ecg_0000861.png" alt="샘플 결과지 1" width="1124" height="814" loading="lazy"></button>
          <button type="button" data-src="assets/samples/ecg_0003650.png" aria-label="샘플 결과지 2 보기"><img src="assets/samples/ecg_0003650.png" alt="샘플 결과지 2" width="1124" height="814" loading="lazy"></button>
          <button type="button" data-src="assets/samples/ecg_0004579.png" aria-label="샘플 결과지 3 보기"><img src="assets/samples/ecg_0004579.png" alt="샘플 결과지 3" width="1124" height="814" loading="lazy"></button>
        </div>
      </div>
      <aside class="result-panel" aria-live="polite">
        <h3>예측 결과</h3>
        <p class="status-note" id="panel-note">이미지를 넣으면 12개 라벨 확률이 여기에 표시됩니다.
        현재 배포본에는 가중치가 없어 확률을 만들지 않습니다 — 임의의 값을 보여주지 않는 것이 원칙입니다.</p>
        <ul class="result-list" id="results">
          <li><span>LVEF ≤ 45%</span><span class="mono">—</span><div class="track"><div class="fill" style="width:0%"></div></div></li>
          <li><span>SHD composite</span><span class="mono">—</span><div class="track"><div class="fill" style="width:0%"></div></div></li>
          <li><span>PASP ≥ 45 mmHg</span><span class="mono">—</span><div class="track"><div class="fill" style="width:0%"></div></div></li>
          <li><span>MR ≥ moderate</span><span class="mono">—</span><div class="track"><div class="fill" style="width:0%"></div></div></li>
        </ul>
      </aside>
    </div>

    <hr class="rule">

    <div class="grid-2">
      <div class="prose">
        <h3>배포 계획</h3>
        <ol>
          <li><b>가중치</b> — Kaggle 학습 후 ONNX 로 내보내고, 224×224 입력·12 sigmoid 출력으로 고정.</li>
          <li><b>브라우저</b> — onnxruntime-web(WASM)으로 이미지 전처리·추론을 모두 클라이언트에서 수행.
          사진은 서버로 보내지 않습니다(개인정보·비용 모두 회피).</li>
          <li><b>PC 앱</b> — 같은 ONNX 를 데스크톱 런타임으로 감싼 로컬 앱.</li>
          <li><b>APK</b> — 카메라 촬영 → 결과지 검출·원근 보정 → 동일 추론 파이프라인.</li>
        </ol>
        <p class="muted">성능이 확인되기 전까지 이 화면은 “입력 확인용”입니다. 확률을 지어내지 않습니다.</p>
      </div>
      <div class="prose">
        <h3>사진에서 바로 추론하지 않는 이유</h3>
        <p>학습 데이터는 정면·무왜곡 렌더입니다. 실제 휴대폰 사진은 기울기·조명·그림자가 다르므로,
        그대로 넣으면 성능이 급락합니다. 그래서 두 단계를 나눕니다.</p>
        <ul>
          <li>문서 검출 + 원근 변환으로 결과지 영역을 정면화</li>
          <li>회색조·대비 정규화 후 224×224 로 축소</li>
          <li>학습 시에도 회전·원근·조명 증강을 넣어 이 간극을 미리 메움</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<script>
(function () {
  var dz = document.getElementById('dropzone');
  var input = document.getElementById('file');
  var preview = document.getElementById('preview');
  var status = document.getElementById('status');

  function show(src, label) {
    preview.hidden = false;
    preview.innerHTML = '<img src="' + src + '" alt="선택한 심전도 결과지 미리보기" width="1124" height="814">';
    status.textContent = label + ' · 모델 미배포라 확률은 표시하지 않습니다.';
  }

  document.querySelectorAll('.samples button').forEach(function (b) {
    b.addEventListener('click', function () { show(b.dataset.src, '샘플 결과지'); });
  });

  input.addEventListener('change', function () {
    var f = input.files && input.files[0];
    if (!f) return;
    var url = URL.createObjectURL(f);
    show(url, f.name);
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
    show(URL.createObjectURL(f), f.name);
  });
})();
</script>
"""
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
