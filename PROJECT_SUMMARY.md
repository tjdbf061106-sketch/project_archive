# QSAR Irritation Predictor - 프로젝트 요약

## 📋 프로젝트 개요

Eye & Skin Irritation 독성 예측을 위한 **웹 애플리케이션** 및 **데스크톱 애플리케이션**

### 기술 스택
- **Backend**: Flask
- **Frontend**: HTML/CSS/JavaScript
- **ML**: scikit-learn, RDKit
- **Desktop**: pywebview
- **Report**: reportlab

---

## 🎯 주요 기능

### 1. 독성 예측
- ✅ **Eye Irritation** (Gradient Boosting, ROC-AUC: 0.765)
- ✅ **Skin Irritation** (SVM RBF, ROC-AUC: 0.756)
- ✅ SMILES 코드 입력
- ✅ 실시간 예측
- ✅ 신뢰도 평가 (High/Medium/Low)

### 2. 분자 시각화
- ✅ RDKit 기반 2D 구조 표시
- ✅ 예시 분자 빠른 선택

### 3. PDF 리포트 (VEGA 스타일)
- ✅ **Section 1**: Prediction Summary
  - 예측 결과 테이블
  - 모델 성능 지표
  - Training 데이터 정보
  
- ✅ **Section 2**: Molecular Descriptors
  - 14개 descriptor 값 테이블
  
- ✅ **Section 3**: Applicability Domain
  - **3.1** Similarity-based (Tanimoto, ECFP4)
  - **3.2** Leverage-based (QMRF: h* = x^T (X^T X)^-1 x)
  
- ✅ **Section 4**: References & Disclaimer

### 4. 오프라인 작동
- ✅ 인터넷 연결 불필요
- ✅ 모든 계산 로컬 수행
- ✅ Fingerprint 유사도 계산
- ✅ QMRF 수식 구현

---

## 📂 파일 구조

```
qsar_webapp/
├── 🌐 웹 애플리케이션
│   ├── app.py                      # Flask 백엔드
│   ├── templates/
│   │   └── index.html              # 프론트엔드 UI
│   ├── start.bat                   # 웹 서버 실행
│   └── README.md                   # 웹앱 문서
│
├── 🖥️ 데스크톱 애플리케이션
│   ├── desktop_app.py              # 데스크톱 런처
│   ├── run_desktop.bat             # 데스크톱 실행
│   ├── build_exe.py                # EXE 빌드 스크립트
│   └── DESKTOP_README.md           # 데스크톱 문서
│
├── 📄 리포트 생성
│   ├── report_generator.py         # PDF 생성 모듈
│   └── example_report.pdf          # 샘플 리포트
│
├── 📦 설정 파일
│   ├── requirements.txt            # Python 의존성
│   └── PROJECT_SUMMARY.md          # 이 문서
│
└── 🗂️ 모델 파일 (외부)
    └── C:\Users\UserK\project\Archive\model_binary\
        ├── model_eye.pkl           # Eye irritation 모델
        ├── model_skin.pkl          # Skin irritation 모델
        ├── scaler_eye.pkl          # Eye scaler
        └── scaler_skin.pkl         # Skin scaler
```

---

## 🚀 실행 방법

### 옵션 1: 웹 애플리케이션 (브라우저)

```bash
# 서버 시작
python app.py

# 브라우저에서 접속
http://localhost:5000
```

**장점**:
- ✅ 가벼움
- ✅ 브라우저에서 실행
- ✅ 여러 탭에서 동시 사용 가능

### 옵션 2: 데스크톱 애플리케이션 (네이티브)

```bash
# 직접 실행
python desktop_app.py

# 또는 배치 파일
run_desktop.bat
```

**장점**:
- ✅ 독립 실행형 (브라우저 불필요)
- ✅ 네이티브 Windows 앱
- ✅ 작업 표시줄 아이콘
- ✅ EXE 빌드 가능

### 옵션 3: EXE 배포 (최종 사용자)

```bash
# EXE 빌드
python build_exe.py

# 생성된 EXE 실행
dist\QSAR_Predictor.exe
```

**장점**:
- ✅ Python 설치 불필요
- ✅ 단일 파일 배포
- ✅ 더블클릭으로 실행

---

## 📊 모델 정보

### Eye Irritation Model
| 항목 | 값 |
|------|-----|
| 알고리즘 | Gradient Boosting |
| Threshold | 0.32 |
| ROC-AUC | 0.765 |
| Sensitivity | 81.7% |
| Specificity | 57.0% |

### Skin Irritation Model
| 항목 | 값 |
|------|-----|
| 알고리즘 | SVM (RBF kernel) |
| Threshold | 0.47 |
| ROC-AUC | 0.756 |
| Sensitivity | 76.5% |
| Specificity | 64.8% |

### Training Data
- **출처**: NTP ICE In Vivo data
- **분류**: EPA 4-class → 2-class (Irritant/Non-irritant)
- **Descriptors**: 13 RDKit descriptors + 1 mixture feature

---

## 🔬 Applicability Domain

### 1. Similarity-based Assessment
```python
# Tanimoto Similarity 계산
query_fp = ECFP4(query_mol)
train_fp = ECFP4(train_mol)
similarity = Tanimoto(query_fp, train_fp)

# Threshold: 0.7
in_domain = avg_similarity >= 0.7
```

### 2. Leverage-based Assessment (QMRF)
```python
# QMRF 수식
h* = x^T (X^T X)^-1 x

# Warning threshold
h*_threshold = 3p/n

# 판정
in_domain = h* <= h*_threshold
```

---

## 📝 사용 예시

### 1. 웹에서 예측
1. 브라우저에서 `http://localhost:5000` 접속
2. SMILES 입력: `CCO` (Ethanol)
3. Eye/Skin 선택
4. "독성 예측 시작" 클릭
5. 결과 확인

### 2. 리포트 다운로드
1. 예측 완료 후
2. "📄 PDF 리포트 다운로드" 버튼 클릭
3. VEGA 스타일 PDF 자동 저장

### 3. 예시 분자
- **Ethanol** (CCO) → Non-irritant
- **Benzene** (c1ccccc1) → Irritant
- **Phenol** (Oc1ccccc1) → Irritant
- **Acetic acid** (CC(=O)O) → Irritant
- **Benzaldehyde** (O=Cc1ccccc1) → Irritant

---

## 📦 설치

### Python 의존성
```bash
pip install -r requirements.txt
```

### 필수 라이브러리
```
Flask>=2.3.0
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
rdkit>=2022.03.1
Pillow>=9.0.0
reportlab>=3.6.0
pywebview>=4.0.0
```

---

## 🎨 UI/UX

### 디자인
- 그라데이션 배경 (#667eea → #764ba2)
- 카드 기반 레이아웃
- 애니메이션 효과 (fadeIn, slideIn)
- 반응형 디자인

### 색상 코딩
- **Non-irritant**: 초록색 (#27ae60)
- **Irritant**: 빨간색 (#e74c3c)
- **High Confidence**: 초록 배지
- **Medium Confidence**: 노란 배지
- **Low Confidence**: 빨간 배지

---

## 🔧 커스터마이징

### 모델 경로 변경
`app.py`:
```python
MODEL_DIR = Path(r"C:\Users\UserK\project\Archive\model_binary")
```

### UI 테마 변경
`templates/index.html`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Threshold 조정
`app.py`:
```python
'eye': {'threshold': 0.32},
'skin': {'threshold': 0.47}
```

---

## ⚠️ 주의사항

1. **모델 버전**: scikit-learn 버전 차이로 인한 경고 무시 가능
2. **In Vivo 데이터**: In vitro 데이터는 포함되지 않음
3. **Binary 분류**: EPA 4-class를 2-class로 단순화
4. **참고용**: 실험 결과를 대체할 수 없음
5. **AD 평가**: 도메인 외부 예측은 주의 필요

---

## 🐛 알려진 이슈

1. **scikit-learn 버전 경고**: 모델 학습 시 1.8.0, 현재 1.7.2 사용
   - 해결: 경고 무시하거나 scikit-learn 업그레이드
   
2. **Unicode 인코딩**: Windows cp949 환경
   - 해결: UTF-8 출력 대신 ASCII 사용

---

## 📈 향후 개선 사항

- [ ] 실제 Training 데이터 로드 (현재 예시 데이터)
- [ ] Batch 예측 (여러 분자 동시 처리)
- [ ] 예측 히스토리 저장
- [ ] 사용자 정의 Threshold
- [ ] 다국어 지원
- [ ] 로고 및 아이콘 추가
- [ ] Auto-update 기능

---

## 📞 지원

문제 발생 시:
1. 로그 파일 확인 (`app.log`, `desktop_app.log`)
2. 콘솔 출력 확인
3. 모델 파일 경로 확인
4. Python 버전 확인 (3.10 권장)

---

## 📄 라이선스

내부 사용 전용

---

## 🙏 감사의 말

- **VEGA**: 리포트 형식 참고
- **NTP ICE**: Training 데이터 제공
- **RDKit**: 분자 처리 및 descriptor 계산
- **scikit-learn**: ML 모델
- **Flask & pywebview**: 웹/데스크톱 프레임워크

---

**Version**: 1.0  
**Date**: 2026-06-29  
**Author**: QSAR Team  
**Contact**: [내부 연락처]
