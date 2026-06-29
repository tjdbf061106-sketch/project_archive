"""
QSAR Irritation Prediction Web App
Flask 기반 독성 예측 웹 애플리케이션
"""

from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from pathlib import Path
import sys

# RDKit imports
try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Draw, Descriptors
    from rdkit.ML.Descriptors import MoleculeDescriptors
    import io
    import base64
    RDLogger.DisableLog('rdApp.*')
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("Warning: RDKit not available. Install with: pip install rdkit")

app = Flask(__name__)

# 모델 디렉토리 설정
MODEL_DIR = Path(r"C:\Users\UserK\project\Archive\model_binary")

# 전역 변수로 모델 저장
models_cache = None

def load_models():
    """모델 및 스케일러 로드"""
    global models_cache

    if models_cache is not None:
        return models_cache

    try:
        with open(MODEL_DIR / "model_eye.pkl", 'rb') as f:
            model_eye = pickle.load(f)
        with open(MODEL_DIR / "scaler_eye.pkl", 'rb') as f:
            scaler_eye = pickle.load(f)
        with open(MODEL_DIR / "model_skin.pkl", 'rb') as f:
            model_skin = pickle.load(f)
        with open(MODEL_DIR / "scaler_skin.pkl", 'rb') as f:
            scaler_skin = pickle.load(f)

        models_cache = {
            'eye': {'model': model_eye, 'scaler': scaler_eye, 'threshold': 0.32},
            'skin': {'model': model_skin, 'scaler': scaler_skin, 'threshold': 0.47}
        }
        return models_cache
    except Exception as e:
        print(f"Error loading models: {e}")
        return None

def compute_descriptors(smiles, mixture=False):
    """RDKit descriptor 계산 (mixture feature 포함)"""
    if not RDKIT_AVAILABLE:
        return None, "RDKit is not installed"

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, "Invalid SMILES"

    descriptor_names = [
        'MolWt', 'MolLogP', 'TPSA', 'NumHAcceptors', 'NumHDonors',
        'NumRotatableBonds', 'NumAromaticRings', 'FractionCSP3',
        'NumHeteroatoms', 'NumSaturatedRings', 'NumAliphaticRings',
        'RingCount', 'HeavyAtomCount'
    ]

    try:
        calc = MoleculeDescriptors.MolecularDescriptorCalculator(descriptor_names)
        desc_values = calc.CalcDescriptors(mol)
        descriptors = np.array(desc_values).reshape(1, -1)

        # mixture feature 추가 (0 = pure compound, 1 = mixture)
        mixture_feature = np.array([[1 if mixture else 0]])
        features = np.hstack([descriptors, mixture_feature])

        return features, None
    except Exception as e:
        return None, f"Descriptor calculation failed: {str(e)}"

def draw_molecule_base64(smiles):
    """분자 구조를 Base64 인코딩된 이미지로 변환"""
    if not RDKIT_AVAILABLE:
        return None

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    img = Draw.MolToImage(mol, size=(300, 300))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

def predict_irritation(smiles, dataset, models_dict, mixture=False):
    """독성 예측"""
    # Descriptor 계산 (mixture feature 포함)
    features, error = compute_descriptors(smiles, mixture=mixture)
    if error:
        return None, error

    # 모델 가져오기
    model_info = models_dict[dataset]
    model = model_info['model']
    scaler = model_info['scaler']
    threshold = model_info['threshold']

    try:
        # Scaling
        X_scaled = scaler.transform(features)

        # 예측
        probability = model.predict_proba(X_scaled)[0][1]
        prediction = 1 if probability >= threshold else 0

        # 신뢰도 계산
        distance_from_threshold = abs(probability - threshold)
        if distance_from_threshold > 0.3:
            confidence = 'High'
        elif distance_from_threshold > 0.15:
            confidence = 'Medium'
        else:
            confidence = 'Low'

        return {
            'prediction': 'Irritant' if prediction == 1 else 'Non-irritant',
            'probability': float(probability),
            'confidence': confidence,
            'threshold': threshold,
            'safe_probability': float(1 - probability)
        }, None

    except Exception as e:
        return None, f"Prediction failed: {str(e)}"

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """예측 API 엔드포인트"""
    try:
        data = request.get_json()
        smiles = data.get('smiles', '').strip()
        predict_types = data.get('predict_types', [])

        if not smiles:
            return jsonify({'error': 'SMILES를 입력해주세요'}), 400

        if not predict_types:
            return jsonify({'error': '예측 타입을 선택해주세요'}), 400

        # 모델 로드
        models_dict = load_models()
        if models_dict is None:
            return jsonify({'error': '모델을 로드할 수 없습니다'}), 500

        # SMILES 유효성 검사
        if RDKIT_AVAILABLE:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return jsonify({'error': '유효하지 않은 SMILES 코드입니다'}), 400

        # 분자 이미지 생성
        mol_image = draw_molecule_base64(smiles) if RDKIT_AVAILABLE else None

        # 예측 수행
        results = {}

        if 'eye' in predict_types:
            result, error = predict_irritation(smiles, 'eye', models_dict)
            if error:
                return jsonify({'error': f'Eye prediction failed: {error}'}), 500
            results['eye'] = result

        if 'skin' in predict_types:
            result, error = predict_irritation(smiles, 'skin', models_dict)
            if error:
                return jsonify({'error': f'Skin prediction failed: {error}'}), 500
            results['skin'] = result

        return jsonify({
            'success': True,
            'smiles': smiles,
            'molecule_image': mol_image,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """헬스체크 엔드포인트"""
    models_dict = load_models()
    return jsonify({
        'status': 'ok',
        'models_loaded': models_dict is not None,
        'rdkit_available': RDKIT_AVAILABLE
    })

if __name__ == '__main__':
    print("=" * 60)
    print("QSAR Irritation Predictor Web App")
    print("=" * 60)
    print(f"Models directory: {MODEL_DIR}")
    print(f"RDKit available: {RDKIT_AVAILABLE}")

    # 모델 로드 확인
    models = load_models()
    if models:
        print("[OK] Models loaded successfully")
    else:
        print("[ERROR] Failed to load models")

    print("=" * 60)
    print("Starting server at http://localhost:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
