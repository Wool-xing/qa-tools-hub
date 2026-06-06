"""Tests to fill coverage gaps in levels.py sandbox and edge cases."""
import pytest
from app.sandbox import run_code_sandbox, SandboxValidator, validate_code_safety


# ── Sandbox AST validation gaps ──

def test_sandbox_rejects_import():
    with pytest.raises(ValueError, match="import"):
        validate_code_safety("import os\nprint(os.getcwd())")


def test_sandbox_rejects_from_import():
    with pytest.raises(ValueError, match="import"):
        validate_code_safety("from os import getcwd\nprint(getcwd())")


def test_sandbox_rejects_class_def():
    with pytest.raises(ValueError, match="class"):
        validate_code_safety("class Foo:\n    pass")


def test_sandbox_rejects_forbidden_builtin():
    with pytest.raises(ValueError, match="not allowed"):
        validate_code_safety("exec('print(1)')")


def test_sandbox_rejects_dunder_access():
    with pytest.raises(ValueError, match="not allowed"):
        validate_code_safety("x = ''.__class__.__subclasses__()\nprint(x)")


def test_sandbox_allows_safe_code():
    validate_code_safety("x = [1,2,3]; print(sum(x))")
    validate_code_safety("for i in range(5):\n    print(i)")
    validate_code_safety("print(__name__)")  # benign dunder should be allowed


def test_run_code_sandbox_invalid_utf8():
    """Test that invalid test_input doesn't crash the sandbox."""
    result = run_code_sandbox("print('ok')", timeout_sec=2)
    assert result["ok"] is True
    assert "ok" in result["stdout"]


# ── Code submission paths ──

def test_code_submit_with_expected_match():
    """Code that produces output matching expected string."""
    result = run_code_sandbox("print('hello')")
    assert result["ok"] is True
    assert result["stdout"] == "hello"


def test_code_submit_clean_exit():
    """Code that exits cleanly without output."""
    result = run_code_sandbox("x = 1 + 1")
    assert result["ok"] is True
    assert result["returncode"] == 0


# ── Labs coverage gaps ──

def test_is_safe_sql_blocks_drop():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("DROP TABLE users") is False


def test_is_safe_sql_blocks_insert():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("INSERT INTO users VALUES (1)") is False


def test_is_safe_sql_blocks_update():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("UPDATE users SET name='x'") is False


def test_is_safe_sql_blocks_delete():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("DELETE FROM users") is False


def test_is_safe_sql_allows_select():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("SELECT * FROM users") is True
    assert is_safe_sql("SELECT COUNT(*) FROM bugs GROUP BY module") is True


def test_is_safe_sql_strips_comments():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("SELECT * FROM users --DROP TABLE users") is True


def test_is_safe_sql_strips_block_comments():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("SELECT * FROM users /* DROP TABLE users */") is True


def test_is_safe_sql_rejects_after_comment_strip():
    from app.lab_data import is_safe_sql
    assert is_safe_sql("-- harmless comment\nDROP TABLE users") is False


# ── CMD simulator gaps ──

def test_sim_grep_case_insensitive():
    from app.lab_data import sim_grep
    result = sim_grep("error", "Error found\nERROR also\nno match", "i")
    assert "Error found" in result
    assert "ERROR also" in result


def test_sim_grep_invert():
    from app.lab_data import sim_grep
    result = sim_grep("error", "Error line\nOK line", "iv")
    assert "OK line" in result


def test_sim_grep_count():
    from app.lab_data import sim_grep
    result = sim_grep("ERROR", "ERROR line\nERROR again\nOK", "c")
    assert "2" in result


def test_sim_grep_regex():
    from app.lab_data import sim_grep
    result = sim_grep(r"\d{3}", "abc 123 def 456 ghi", "")
    assert "123" in result
    assert "456" in result


def test_sim_grep_invalid_regex_fallback():
    from app.lab_data import sim_grep
    result = sim_grep("[invalid(regex", "hello [invalid(regex world", "")
    assert "invalid" in result.lower() or "hello" in result.lower()
