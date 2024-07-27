from flask import Flask, request, jsonify
import os
import subprocess
import time
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Quiz
from contextlib import contextmanager

app = Flask(__name__)

# MySQL 데이터베이스 설정
from config import DATABASE_URI

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# 언어별 파일 확장자와 실행 명령어
EXTENSIONS = {
    'python': 'py',
    'java': 'java'
}

COMMANDS = {
    'python': 'python',
    'java': 'java'
}

# 파일 저장 경로
PYTHON_DIR = 'python_files'
JAVA_DIR = 'java_files'

# 제한 시간 설정 (초)
TIME_LIMIT = 5

@app.route('/code/run_code', methods=['POST'])
def run_code():
    data = request.json
    user_id = data['user_id']
    code = data['code']
    language = data['language']
    quiz_id = data['quiz_id']

    # 확장자와 명령어 결정
    ext = EXTENSIONS.get(language)
    command = COMMANDS.get(language)
    if not ext or not command:
        return jsonify({'error': 'Unsupported language'}), 400

    # 파일 저장
    if language == 'python' and not os.path.exists(PYTHON_DIR):
        os.makedirs(PYTHON_DIR)
    if language == 'java' and not os.path.exists(JAVA_DIR):
        os.makedirs(JAVA_DIR)

    # 고유 파일 이름 생성
    unique_id = str(uuid.uuid4())
    if language == 'java':
        java_dir = f"{JAVA_DIR}/java_files_{unique_id}"
        if not os.path.exists(java_dir):
            os.makedirs(java_dir)
        java_filename = f"{java_dir}/Main.java"
        with open(java_filename, 'w') as f:
            f.write(code)
    elif language == 'python':
        python_filename = f"{PYTHON_DIR}/code_{language}_{user_id}_{quiz_id}_{unique_id}.{ext}"
        with open(python_filename, 'w') as f:
            f.write(code)

    # DB에서 입력값과 예상 출력값 가져오기
    with session_scope() as session:
        quiz = session.query(Quiz).filter_by(quiz_id=quiz_id).first()
        if not quiz:
            if language == 'python' and os.path.exists(python_filename):
                os.remove(python_filename)  # python 파일 삭제
            if language == 'java' and os.path.exists(java_filename):
                os.remove(java_filename)  # Java 파일 삭제
                os.rmdir(java_dir)  # Java 디렉터리 삭제
            return jsonify({'error': 'Quiz not found'}), 404

        inputs = quiz.inputs
        expected_outputs = quiz.outputs.strip().split('\n')

    # 코드 실행
    try:
        if language == 'python':
            process = subprocess.Popen(f"python {python_filename}", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        elif language == 'java':
            # Java 컴파일
            compile_process = subprocess.Popen(f"javac {java_filename}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            compile_stdout, compile_stderr = compile_process.communicate()

            if compile_stderr:
                return jsonify({'result': f'오류 발생 {compile_stderr}'}), 200

            # Java 실행
            process = subprocess.Popen(f"java -cp {java_dir} Main", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            return jsonify({'error': 'Unsupported language'}), 400

        start_time = time.time()
        stdout, stderr = process.communicate(input=inputs.encode('utf-8'), timeout=TIME_LIMIT)
        end_time = time.time()
        
        if end_time - start_time > TIME_LIMIT:
            process.kill()
            return jsonify({'result': '시간 초과'}), 200

        if stderr:
            return jsonify({'result': f'오류 발생 {stderr}'}), 200

        output = stdout.decode().strip().split('\n')

        # 결과 비교
        if output == expected_outputs:
            result = '정답'
        else:
            result = '오답'

        return jsonify({'result': result}), 200

    except subprocess.TimeoutExpired:
        process.kill()
        return jsonify({'result': '시간 초과'}), 200

    finally:
        # 파일 삭제 (성공적인 실행 후)
        if language == 'python' and os.path.exists(python_filename):
            os.remove(python_filename)
        if language == 'java':
            java_classfile = f"{java_dir}/Main.class"
            if os.path.exists(java_filename):
                os.remove(java_filename)
            if os.path.exists(java_classfile):
                os.remove(java_classfile)
            if os.path.exists(java_dir):
                os.rmdir(java_dir)  # Java 디렉터리 삭제

if __name__ == '__main__':
    app.run(debug=True)
