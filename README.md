# QSAR Irritation Predictor Web App

Flask 기반 Eye & Skin Irritation 독성 예측 웹 애플리케이션

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 앱 실행

```bash
python app.py
```

### 3. 브라우저에서 접속

```
http://localhost:5000
```

## 📁 프로젝트 구조

```
qsar_webapp/
├── app.py                 # Flask 애플리케이션
├── templates/
│   └── index.html        # 프론트엔드 UI
├── requirements.txt      # 의존성 목록
└── README.md            # 이 문서
```

## 🎯 주요 기능

1. **👁️ Eye Irritation 예측** - Gradient Boosting (ROC-AUC: 0.765)
2. **🖐️ Skin Irritation 예측** - SVM RBF kernel (ROC-AUC: 0.756)
3. **분자 구조 시각화** - RDKit 기반
4. **실시간 예측** - SMILES 입력 즉시 예측
5. **신뢰도 표시** - High/Medium/Low 신뢰도 수준
6. **📄 VEGA 스타일 PDF 리포트 생성**
   - Prediction Summary (모델 예측 결과 + Training 정보)
   - Molecular Descriptors (분자 특성)
   - Applicability Domain (3.1 Similarity-based + 3.2 Leverage-based QMRF)
   - References & Disclaimer

## 📊 모델 정보

### Eye Irritation Model
- 알고리즘: Gradient Boosting
- Threshold: 0.32
- ROC-AUC: 0.765
- Sensitivity: 81.7%
- Specificity: 57.0%

### Skin Irritation Model
- 알고리즘: SVM (RBF kernel)
- Threshold: 0.47
- ROC-AUC: 0.756
- Sensitivity: 76.5%
- Specificity: 64.8%

## 💡 사용 방법

1. 예시 분자 버튼 클릭 또는 SMILES 직접 입력
2. Eye/Skin 예측 대상 선택
3. "독성 예측 시작" 버튼 클릭
4. 결과 확인

## 🔧 API 엔드포인트

### POST /predict

**Request:**
```json
{
  "smiles": "CCO",
  "predict_types": ["eye", "skin"]
}
```

**Response:**
```json
{
  "success": true,
  "smiles": "CCO",
  "molecule_image": "data:image/png;base64,...",
  "results": {
    "eye": {
      "prediction": "Non-irritant",
      "probability": 0.25,
      "confidence": "High",
      "threshold": 0.32,
      "safe_probability": 0.75
    },
    "skin": {
      "prediction": "Non-irritant",
      "probability": 0.30,
      "confidence": "Medium",
      "threshold": 0.47,
      "safe_probability": 0.70
    }
  }
}
```

### GET /health

헬스체크 엔드포인트

**Response:**
```json
{
  "status": "ok",
  "models_loaded": true,
  "rdkit_available": true
}
```

## ⚠️ 주의사항

- 이 예측은 참고용이며 실제 실험 결과를 대체할 수 없습니다
- In Vivo 데이터만 학습되었으며 In vitro 데이터는 포함되지 않음
- Binary 분류로 EPA 4-class를 단순화함

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 등록해주세요.
