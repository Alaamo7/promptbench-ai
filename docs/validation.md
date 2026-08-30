# Validation

Audit date: 2026-08-30. Offline environment: Python 3.12.13. Live provider credentials were not used during the GitHub mirror.

| Test | Expected | Actual | Status | Evidence |
|---|---|---|---|---|
| Source tree inspection | Runtime, entry point, providers, dependencies and tests identified | Gradio/app.py, Hugging Face + Ollama, requirements and 29 original tests identified | PASS | `README.md`, `src/`, `requirements.txt`, HF commit `fd64045` |
| Python compilation | Application, source and tests compile | `python -m compileall -q app.py src tests` exited 0 | PASS | Local command output, 2026-08-30 |
| Offline pytest suite | No external credential/API required; all tests pass | 35 tests passed; 1 opt-in integration test deselected | PASS | CI command and local pytest output |
| Dependency consistency | Installed packages have no broken requirements | `python -m pip check`: no broken requirements | PASS | Local command output |
| Empty prompt | Rejected before API call | Gradio error asserted with mocked client | PASS | `tests/test_app_mvp.py` |
| Malformed rules JSON | Rejected before API call | Gradio error asserted | PASS | `tests/test_app_mvp.py` |
| Extremely long response | Deterministic maximum-word rule fails predictably | 20,000-word case returns `max_words_pass=False` | PASS | `tests/test_edge_cases.py` |
| Malformed evaluator output | Invalid/non-object judge data rejected | ValueError asserted | PASS | `tests/test_evaluator.py`, `tests/test_edge_cases.py` |
| Missing Hugging Face key | Configuration validation fails clearly | RuntimeError asserted when backend is Hugging Face and token is empty | PASS | `tests/test_security.py` |
| Target timeout/failure | UI wraps failure without claiming success | Simulated timeout becomes Gradio execution error | PASS | `tests/test_app_mvp.py` |
| Batch partial failure | Remaining cases continue; failed case stays zero-score/FAILED | Behavior asserted | PASS | `tests/test_benchmark.py` |
| Same-case comparison | Models receive identical ordered cases; scoped winner ranked | Behavior asserted | PASS | `tests/test_comparison.py` |
| Dataset integrity | At least 50 unique valid bilingual cases | 50-case checks pass | PASS | `tests/test_phase3_dataset.py` |
| `.env` protection | `.env` ignored; example contains no credential value | Assertions pass | PASS | `tests/test_security.py` |
| Hardcoded secret patterns | No common live-token prefixes or literal secret assignments | Current clean mirror passes scan | PASS | `tests/test_security.py` |
| Historical public credential | Removed value is also revoked/rotated | Rotation cannot be verified from source | PARTIAL | Historical secret alert; see security issue |
| Live Hugging Face UI | Public interface exists | Genuine screenshots verified; Space observed sleeping | PARTIAL | `docs/assets/phase6_*.png`, live Space |
| Live target/evaluator API | Authorized target response and judge result returned now | Not executed during mirror; no credential used | NOT TESTED | Opt-in integration workflow only |
| CI run on GitHub | Offline test, dependency, syntax and secret jobs complete | Pending first GitHub Actions run | NOT TESTED | `.github/workflows/ci.yml` |

## Coverage by requested category

- Functional: evaluator scoring, deterministic penalties, benchmark metrics/filtering/error continuation, analytics, comparison fairness/ranking, history/export/report generation.
- Edge cases: empty input, malformed rules/judge data, extremely long text, duplicate model names, empty datasets.
- Failure handling: missing credential, target timeout, invalid evaluator output, per-case API failure.
- Security: ignored `.env`, blank example credential, common token-prefix scan, hardcoded-assignment scan, CI Gitleaks.

No test is marked PASS unless it was executed offline or its asserted behavior was directly exercised by the suite.
