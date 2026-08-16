"""Secure Python code sandbox for QA通关.

AST-level validation + subprocess isolation with restricted builtins.
IMPORTANT: This sandbox relies primarily on AST validation. Production deployments
should add OS-level isolation (Docker seccomp/AppArmor profiles, cgroup resource limits).
"""

import ast
import subprocess
import os
import sys
import platform
import tempfile


def _safe_type(obj):
    """Type introspection only — blocks the 3-argument class-creation form."""
    return type(obj)


FORBIDDEN_BUILTINS = frozenset({
    'exec', 'eval', 'compile', '__import__', 'open', 'breakpoint',
    'globals', 'locals', 'vars', 'dir', 'getattr',
    'setattr', 'delattr', 'hasattr',
})

# Only block dangerous dunders — allow benign ones like __name__, __doc__
DANGEROUS_DUNDERS = frozenset({
    '__import__', '__subclasses__', '__globals__', '__code__', '__closure__',
    '__reduce__', '__reduce_ex__', '__getstate__', '__setstate__',
    '__class_getitem__', '__init_subclass__', '__build_class__',
})

SAFE_BUILTINS = {
    'print': print, 'len': len, 'range': range, 'int': int, 'str': str,
    'float': float, 'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple,
    'set': set, 'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
    'sorted': sorted, 'reversed': reversed, 'enumerate': enumerate, 'zip': zip,
    'map': map, 'filter': filter, 'type': _safe_type, 'isinstance': isinstance,
    'input': input, 'repr': repr, 'format': format,
    'True': True, 'False': False, 'None': None,
    'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
    'KeyError': KeyError, 'IndexError': IndexError, 'StopIteration': StopIteration,
    'ZeroDivisionError': ZeroDivisionError,
}

SANDBOX_WRAPPER = """\
import sys as _sys
_orig = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
_safe = __SAFE_KEYS__
__builtins__ = {k: _orig[k] for k in _safe if k in _orig}
del _sys, _orig, _safe
"""


class SandboxValidator(ast.NodeVisitor):
    """AST validator that rejects dangerous code constructs."""

    def visit_Import(self, node):
        raise ValueError("import statements are not allowed in sandbox")

    def visit_ImportFrom(self, node):
        raise ValueError("import statements are not allowed in sandbox")

    def visit_ClassDef(self, node):
        raise ValueError("class definitions are not allowed in sandbox")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_BUILTINS:
            raise ValueError(f"{node.func.id}() is not allowed in sandbox")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.attr, str) and node.attr in DANGEROUS_DUNDERS:
            raise ValueError(f"{node.attr} is not allowed in sandbox")
        self.generic_visit(node)


def validate_code_safety(code: str):
    """Raise ValueError if code contains forbidden constructs."""
    tree = ast.parse(code)
    SandboxValidator().visit(tree)


def run_code_sandbox(code: str, test_input: str = "", timeout_sec: int | None = None) -> dict:
    """Execute Python code in subprocess sandbox with timeout.

    Security: AST validation blocks imports, class definitions, dunder access,
    and dangerous builtins (exec, eval, __import__, open, etc.).
    The subprocess runs with restricted __builtins__ as defense-in-depth.
    """
    try:
        validate_code_safety(code)
    except (SyntaxError, ValueError) as e:
        return {"ok": False, "error": str(e)}

    safe_keys_set = repr(sorted(SAFE_BUILTINS.keys()))
    wrapped_code = SANDBOX_WRAPPER.replace("__SAFE_KEYS__", safe_keys_set) + "\n" + code

    from app.config import SANDBOX_TIMEOUT
    if timeout_sec is None:
        timeout_sec = SANDBOX_TIMEOUT
    try:
        kwargs = {
            "input": test_input, "capture_output": True, "text": True,
            "timeout": timeout_sec,
            "env": {"PYTHONPATH": "", "PYTHONSTARTUP": "", "PYTHONHOME": "",
                    "PATH": os.environ.get("PATH", ""),
                    "HOME": os.environ.get("HOME", tempfile.gettempdir())},
        }
        if platform.system() == "Windows":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["preexec_fn"] = os.setpgrp
        proc = subprocess.run([sys.executable, "-c", wrapped_code], **kwargs)
        return {"ok": True, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip(), "returncode": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Code execution timed out (>{timeout_sec}s)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
