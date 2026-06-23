@echo off
echo ==========================================
echo ?? COMPLANT - Analise Fitoquimica
echo ==========================================
echo.

cd /d C:\Users\carl\apk_quim_plant

echo ?? Pasta: %cd%
echo.
echo ?? Verificando conexao com GitHub...
echo.

REM Testar se o JSON est? acess?vel
curl -s -o nul -w "%%{http_code}" https://raw.githubusercontent.com/Carl0000oak/apk_quim_plant/main/complant/data/compounds.json > temp.txt
set /p status=<temp.txt
del temp.txt

if "%status%"=="200" (
    echo ? JSON acessivel no GitHub!
) else (
    echo ? JSON NAO acessivel! Status: %status%
    echo.
    echo ?? Verifique se o arquivo esta no GitHub:
    echo https://raw.githubusercontent.com/Carl0000oak/apk_quim_plant/main/complant/data/compounds.json
    echo.
    pause
    exit /b
)

echo.
echo ==========================================
echo ?? Executando testes...
echo ==========================================
echo.

python testar.py

echo.
echo ==========================================
echo ? Teste concluido!
echo ==========================================
pause
