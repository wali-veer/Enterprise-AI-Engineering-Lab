# Development Notes

## Running Lab-01

If you encounter the following error:

```text
ModuleNotFoundError: No module named 'common'
```

or

```text
ModuleNotFoundError: No module named 'src'
```

set the repository root as `PYTHONPATH` before running the lab.

PowerShell:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python '\utilities\lab01_token_usage.py
```

This is a temporary workaround during the early development of the project.

A future sprint will package the project properly so that no environment configuration is required.