@echo off

if "%1"=="build" (
    pyinstaller --onefile youtube_download.py
) else if "%1"=="download_sample" (
    python youtube_download.py https://www.youtube.com/watch?v=NUC2EQvdzmY
) else (
    python youtube_download.py %*
)
