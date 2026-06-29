# QSAR Irritation Predictor - Desktop Application

Windows 네이티브 데스크톱 애플리케이션 버전

## 🚀 빠른 시작

### 방법 1: Python으로 실행

```bash
# 의존성 설치 (최초 1회)
pip install -r requirements.txt

# 데스크톱 앱 실행
python desktop_app.py
```

또는 배치 파일 더블클릭:
```
run_desktop.bat
```

### 방법 2: EXE 파일로 빌드 (배포용)

```bash
# PyInstaller 설치
pip install pyinstaller

# EXE 빌드
python build_exe.py

# 생성된 EXE 실행
dist\QSAR_Predictor.exe
```

## 📦 기술 스택

- **GUI**: pywebview (네이티브 Windows WebView2)
- **Backend**: Flask
- **ML**: scikit-learn, RDKit
- **PDF**: reportlab

## 🎯 주요 특징

### 1. 네이티브 데스크톱 앱
- ✅ Windows 네이티브 창 (WebView2 기반)
- ✅ 브라우저 없이 독립 실행
- ✅ 작업 표시줄에 아이콘 표시
- ✅ 최소화/최대화/닫기 버튼

### 2. 완전한 오프라인 작동
- ✅ 인터넷 연결 불필요
- ✅ 모든 계산이 로컬에서 수행
- ✅ 모델 파일 포함

### 3. 전체 기능 지원
- ✅ Eye & Skin Irritation 예측
- ✅ 분자 구조 시각화
- ✅ VEGA 스타일 PDF 리포트 생성
- ✅ Applicability Domain 평가

## 🖼️ 화면 구성

```
┌─────────────────────────────────────────────┐
│  QSAR Irritation Predictor         _ □ X   │
├─────────────────────────────────────────────┤
│                                             │
│  👁️ QSAR Irritation Predictor              │
│  Eye & Skin Irritation 독성 예측 시스템     │
│                                             │
│  📝 화합물 정보 입력                         │
│  ┌─────────────────────────────────────┐   │
│  │ SMILES: CCO                         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [🔬 독성 예측 시작]                        │
│                                             │
│  📊 예측 결과                                │
│  ┌─────────────────────────────────────┐   │
│  │ ✅ Non-irritant                     │   │
│  │ 자극성 확률: 25.0%                   │   │
│  │ 신뢰도: High                        │   │
│  │ [📄 PDF 리포트 다운로드]             │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

## 📁 프로젝트 구조

```
qsar_webapp/
├── desktop_app.py           # 데스크톱 앱 런처
├── app.py                   # Flask 백엔드
├── report_generator.py      # PDF 리포트 생성
├── templates/
│   └── index.html          # 프론트엔드 UI
├── run_desktop.bat         # 실행 배치 파일
├── build_exe.py            # EXE 빌드 스크립트
├── requirements.txt        # Python 의존성
└── README.md
```

## 🔧 EXE 빌드 상세

### 포함되는 파일
- 모든 Python 코드
- ML 모델 (model_eye.pkl, model_skin.pkl)
- Scaler (scaler_eye.pkl, scaler_skin.pkl)
- HTML 템플릿
- Python 런타임 및 라이브러리

### 빌드 옵션
```python
--onefile          # 단일 EXE 파일
--windowed         # 콘솔 창 숨김
--add-data         # 데이터 파일 포함
--hidden-import    # 숨겨진 import 포함
```

### 빌드 결과
- **파일**: `dist/QSAR_Predictor.exe`
- **크기**: 약 200-300MB (모든 의존성 포함)
- **실행**: 더블클릭으로 즉시 실행

## 💡 사용 방법

### 1. 애플리케이션 시작
```bash
python desktop_app.py
```
또는
```bash
run_desktop.bat
```

### 2. 예측 수행
1. SMILES 코드 입력 (예: CCO, c1ccccc1)
2. 예측 대상 선택 (Eye/Skin)
3. "독성 예측 시작" 버튼 클릭

### 3. 리포트 다운로드
1. 예측 완료 후
2. "📄 PDF 리포트 다운로드" 버튼 클릭
3. VEGA 스타일 리포트 자동 저장

## ⚙️ 설정

### 윈도우 크기
`desktop_app.py`에서 수정:
```python
width=1400,        # 너비
height=900,        # 높이
min_size=(1000, 700),  # 최소 크기
```

### 포트 변경
자동으로 사용 가능한 포트 찾기 (5000-5010)

## 🐛 문제 해결

### 1. "Port already in use" 오류
```bash
# 다른 Flask 프로세스 종료
taskkill /F /IM python.exe
```

### 2. 모델 로드 실패
- 모델 파일 경로 확인: `C:\Users\UserK\project\Archive\model_binary\`
- `app.py`의 `MODEL_DIR` 경로 수정

### 3. pywebview 오류
```bash
# pythonnet 재설치
pip uninstall pythonnet
pip install pythonnet
```

### 4. EXE 빌드 실패
```bash
# PyInstaller 재설치
pip uninstall pyinstaller
pip install pyinstaller
```

## 📊 성능

- **시작 시간**: 3-5초
- **예측 속도**: < 1초
- **메모리 사용**: 약 200-300MB
- **CPU 사용**: 예측 시에만 증가

## 🔒 보안

- ✅ 로컬 실행 (외부 통신 없음)
- ✅ 데이터 외부 전송 없음
- ✅ 모든 계산이 로컬에서 수행

## 📝 라이선스

내부 사용 전용

## 🆘 지원

문제 발생 시:
1. `desktop_app.log` 파일 확인
2. 콘솔 출력 확인
3. 이슈 리포트 작성

## 🔄 업데이트

### 모델 업데이트
1. `C:\Users\UserK\project\Archive\model_binary\` 에 새 모델 파일 배치
2. 앱 재시작

### 코드 업데이트
1. Python 코드 수정
2. 앱 재시작 (또는 EXE 재빌드)

## 🎨 커스터마이징

### UI 테마 변경
`templates/index.html` 수정:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### 로고 추가
1. 로고 이미지 준비 (PNG, 512x512)
2. `build_exe.py`에서 `--icon=logo.png` 추가

## 📦 배포

### 최종 사용자에게 배포
1. EXE 빌드: `python build_exe.py`
2. `dist/QSAR_Predictor.exe` 파일 전달
3. 사용자는 더블클릭으로 실행

### 필요 사항
- Windows 10 이상
- WebView2 런타임 (Windows 11에 기본 포함)

---

**Version**: 1.0  
**Date**: 2026-06-29  
**Built with**: Python, Flask, pywebview, RDKit, scikit-learn
