import os
import shutil
import stat
import subprocess
import sys
import pytest
from fixes.translate_helper import compile_translations, find_msgfmt, TranslationCompileError

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures', 'translations')


def test_find_msgfmt_via_path():
    # If msgfmt is installed in PATH, find_msgfmt returns it, otherwise returns None
    m = find_msgfmt(None)
    # don't fail the test suite if not present
    assert (m is None) or os.path.isfile(m)


@pytest.mark.skipif(shutil.which('msgfmt') is None, reason='msgfmt not installed in PATH')
def test_compile_success(tmp_path):
    src = os.path.join(FIXTURES)
    out = tmp_path / 'out'
    out.mkdir()

    compile_translations(src, output_dir=str(out))

    mo = out / 'en' / 'LC_MESSAGES' / 'messages.mo'
    assert mo.exists()
    assert mo.stat().st_size > 0


def test_compile_missing_msgfmt(tmp_path):
    src = os.path.join(FIXTURES)
    with pytest.raises(TranslationCompileError) as exc:
        compile_translations(src, msgfmt_path=str(tmp_path / 'no-such-msgfmt'))
    assert 'msgfmt not found' in str(exc.value)


@pytest.mark.skipif(sys.platform.startswith('win'), reason='Permission change not reliable on Windows')
def test_compile_permission_denied(tmp_path):
    src = os.path.join(FIXTURES)
    out = tmp_path / 'out'
    out.mkdir()

    # remove write permissions
    out.chmod(0o555)

    with pytest.raises(TranslationCompileError) as exc:
        compile_translations(src, output_dir=str(out))

    # revert perms to allow cleanup
    out.chmod(0o755)
    assert 'Permission' in str(exc.value) or 'msgfmt failed' in str(exc.value)
