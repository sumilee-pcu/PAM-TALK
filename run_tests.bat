@echo off
echo PAM-TALK 통합 테스트 시스템 실행
echo ====================================

REM Python 가상환경 활성화 (있는 경우)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 가상환경 활성화됨
)

REM 테스트 실행
python run_tests.py

pause