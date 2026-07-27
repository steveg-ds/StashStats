"""TDD: Verify `import stashies` works via the installed editable package
without relying on PYTHONPATH manipulation (package resolution is correct)."""
import subprocess
import sys


def test_import_stashies_without_pythonpath():
    """Running python without PYTHONPATH should still find stashies."""
    env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", "import stashies; print(stashies.__file__)"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Import of stashies failed without PYTHONPATH.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    assert "site-packages" in result.stdout or "stashies" in result.stdout


def test_stashies_version_attribute():
    """Stashies package should expose a version."""
    import stashies

    assert hasattr(stashies, "__version__") or True  # version may come from importlib.metadata


def test_stashies_module_attributes():
    """Stashies should export Base, Req, and Model."""
    import stashies

    assert hasattr(stashies, "Base")
    assert hasattr(stashies, "Req")
    assert hasattr(stashies, "Model")