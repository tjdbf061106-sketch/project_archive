"""
PyInstaller를 사용한 EXE 빌드 스크립트
"""

import PyInstaller.__main__
import sys
from pathlib import Path

def build_exe():
    """EXE 파일 빌드"""

    project_dir = Path(__file__).parent
    model_dir = Path(r"C:\Users\UserK\project\Archive\model_binary")

    # PyInstaller 옵션
    options = [
        'desktop_app.py',  # 메인 스크립트
        '--name=QSAR_Predictor',  # EXE 이름
        '--onefile',  # 단일 EXE 파일
        '--windowed',  # 콘솔 창 숨기기
        '--icon=NONE',  # 아이콘 (없으면 기본)

        # 데이터 파일 포함
        f'--add-data={project_dir / "templates"};templates',
        f'--add-data={model_dir / "model_eye.pkl"};.',
        f'--add-data={model_dir / "scaler_eye.pkl"};.',
        f'--add-data={model_dir / "model_skin.pkl"};.',
        f'--add-data={model_dir / "scaler_skin.pkl"};.',

        # 숨겨진 import
        '--hidden-import=rdkit',
        '--hidden-import=rdkit.Chem',
        '--hidden-import=sklearn',
        '--hidden-import=reportlab',
        '--hidden-import=webview',

        # 출력 디렉토리
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',

        # 기타
        '--clean',
        '--noconfirm',
    ]

    print("=" * 60)
    print("Building EXE with PyInstaller...")
    print("=" * 60)

    try:
        PyInstaller.__main__.run(options)
        print("\n" + "=" * 60)
        print("✓ Build completed!")
        print("EXE location: dist/QSAR_Predictor.exe")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()
