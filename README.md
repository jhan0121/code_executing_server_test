# 프로젝트 설명

## 설정 방법

1. 가상 환경 설정:
    ```sh
    python -m venv venv
    source venv/bin/activate  # 윈도우의 경우 `venv\Scripts\activate`
    ```

2. 필요 패키지 설치:
    ```sh
    pip install -r requirements.txt
    ```

3. 데이터베이스 설정:
    - `config.py` 파일에서 데이터베이스 URI를 설정합니다.

4. 서버 실행:
    ```sh
    set FLASK_APP=app.py
    flask run
    ```

## 실행 방법

서버를 실행한 후, POST 요청을 `/code/run_code` 엔드포인트로 보내 코드를 실행할 수 있습니다.s

## 테스트

테스트를 실행하려면:
```sh
pytest tests/
```