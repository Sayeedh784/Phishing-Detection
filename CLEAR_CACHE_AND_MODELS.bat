
@echo off
echo Deleting __pycache__ and old joblib models...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
if exist backend\ml\models\*.joblib del /q backend\ml\models\*.joblib
echo Done. Now retrain:
echo cd backend
echo python -m ml.train_url
echo python -m ml.train_email
pause
