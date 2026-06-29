"""
QSAR Irritation Predictor - Desktop Application
Flask 웹앱을 데스크톱 애플리케이션으로 래핑
"""

import webview
import threading
import socket
import time
import sys
from pathlib import Path

# Flask 앱 import
from app import app, load_models

def is_port_in_use(port):
    """포트 사용 여부 확인"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_free_port(start_port=5000, max_attempts=10):
    """사용 가능한 포트 찾기"""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    raise RuntimeError("No free ports available")

def start_flask_server(port):
    """Flask 서버를 백그라운드에서 실행"""
    try:
        print(f"[Flask] Starting server on port {port}...")
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"[Flask] Error: {e}")

class DesktopApp:
    """데스크톱 애플리케이션 클래스"""

    def __init__(self):
        self.port = None
        self.window = None
        self.server_thread = None

    def start(self):
        """애플리케이션 시작"""
        print("=" * 60)
        print("QSAR Irritation Predictor - Desktop Application")
        print("=" * 60)

        # 모델 로드 확인
        print("[App] Loading models...")
        models = load_models()
        if models:
            print("[App] Models loaded successfully")
        else:
            print("[App] WARNING: Failed to load models")

        # 사용 가능한 포트 찾기
        try:
            self.port = find_free_port()
            print(f"[App] Using port: {self.port}")
        except RuntimeError as e:
            print(f"[App] ERROR: {e}")
            sys.exit(1)

        # Flask 서버 시작 (백그라운드 스레드)
        self.server_thread = threading.Thread(
            target=start_flask_server,
            args=(self.port,),
            daemon=True
        )
        self.server_thread.start()

        # 서버 시작 대기
        print("[App] Waiting for server to start...")
        max_wait = 10
        for i in range(max_wait):
            if is_port_in_use(self.port):
                print("[App] Server is ready!")
                break
            time.sleep(0.5)
        else:
            print("[App] ERROR: Server failed to start")
            sys.exit(1)

        # pywebview 윈도우 생성
        url = f'http://127.0.0.1:{self.port}'
        print(f"[App] Opening window at {url}")
        print("=" * 60)

        self.window = webview.create_window(
            title='QSAR Irritation Predictor',
            url=url,
            width=1400,
            height=900,
            resizable=True,
            min_size=(1000, 700),
            background_color='#667eea'
        )

        # 윈도우 실행
        webview.start(debug=False)

def main():
    """메인 함수"""
    app_instance = DesktopApp()
    app_instance.start()

if __name__ == '__main__':
    main()
