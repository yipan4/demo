## Scripted AI Outputs (for narration)

- Root cause: `requests` not in `requirements.txt` but imported in `app.py`.
- Suggest patch:
  ```diff
  -flask==0.12
  +flask==2.3.3
  +requests==2.31.0
  ```
- Risk note: Old Flask versions may have known issues; upgrade to maintained release.