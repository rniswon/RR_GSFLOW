rem set PATH=C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37;C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\Library\mingw-w64\bin;C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\Library\usr\bin;C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\Library\bin;C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\Scripts;C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\bin;C:\anaconda\condabin;C:\Oracle\product\11.2.0\client_1;C:\Oracle\product\11.2.0\client_1\bin;C:\ProgramData\Oracle\Java\javapath;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0;C:\Program Files (x86)\Google\Google Apps Sync;C:\Program Files (x86)\Google\Google Apps Migration;C:\ArcGIS\gbin;C:\Program Files\MIT\Kerberos\bin;C:\Program Files (x86)\MIT\Kerberos\bin;C:\Program Files\PuTTY;C:\Program Files\dotnet;C:\WINDOWS\System32\OpenSSH;C:\Users\aalzraiee\AppData\Local\Microsoft\WindowsApps;C:\Users\aalzraiee\AppData\Local\Programs\Git\cmd;C:\Users\aalzraiee\AppData\Local\GitHubDesktop\bin;%PATH%
@echo OFF
rem How to run a Python script in a given conda environment from a batch file.

rem It doesn't require:
rem - conda to be in the PATH
rem - cmd.exe to be initialized with conda init

rem Define here the path to your conda installation
set CONDAPATH=C:\Users\sadera\AppData\Local\Continuum\anaconda3
rem Define here the name of the environment
set ENVNAME=py37

rem The following command activates the base environment.
rem call C:\ProgramData\Miniconda3\Scripts\activate.bat C:\ProgramData\Miniconda3
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

rem Activate the conda environment
rem Using call is required here, see: https://stackoverflow.com/questions/24678144/conda-environments-and-bat-files
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

rem Run a python script in that environment
python ss_forward_model_20210813.py

rem Deactivate the environment
call conda deactivate

rem If conda is directly available from the command line then the following code works.
rem call activate someenv
rem python script.py
rem conda deactivate

rem One could also use the conda run command
rem conda run -n someenv python script.py
rem C:\Users\sadera\AppData\Local\Continuum\anaconda3\envs\py37\python.exe ss_forward_model_20210702.py