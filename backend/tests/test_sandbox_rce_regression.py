"""RCE regression tests for sandbox AST validator (QA-2026-08-18 round 1)."""
import pytest
from app.sandbox import run_code_sandbox, validate_code_safety

POC_CLASS_CHAIN = '''
obj = ().__class__.__base__
subs = obj.__class__.__dict__["__subclasses__"](obj)
wc = [c for c in subs if c.__name__ == "_wrap_close"][0]
ga = obj.__dict__["__getattribute__"]
g = ga(wc.__init__, "__globals__")
g["system"]("echo SANDBOX_ESCAPE_OK")
'''

POC_DIRECT_GETATTRIBUTE = '''
obj = ().__class__
ga = obj.__getattribute__
g = ga(obj, "__class__")
print(g)
'''

POC_SUBSCRIPT_DUNDER = '''
d = {}.__class__.__dict__["__getattribute__"]
print(d)
'''

POC_MRO = '''
m = ().__class__.__mro__
print(len(m))
'''


def test_class_chain_rce_blocked():
    r = run_code_sandbox(POC_CLASS_CHAIN)
    assert r["ok"] is False
    assert "SANDBOX_ESCAPE_OK" not in r.get("stdout", "")


def test_direct_getattribute_attribute_blocked():
    with pytest.raises(ValueError):
        validate_code_safety("obj = ().__class__\nprint(obj.__getattribute__)")


def test_subscript_string_dunder_blocked():
    with pytest.raises(ValueError):
        validate_code_safety('print({}.__class__.__dict__["__getattribute__"])')


def test_class_attribute_blocked():
    with pytest.raises(ValueError):
        validate_code_safety("print(().__class__)")


def test_base_attribute_blocked():
    with pytest.raises(ValueError):
        validate_code_safety("print(().__class__.__base__)")


def test_mro_attribute_blocked():
    with pytest.raises(ValueError):
        validate_code_safety("print(().__class__.__mro__)")


def test_dict_attribute_blocked():
    with pytest.raises(ValueError):
        validate_code_safety("print(().__class__.__dict__)")
