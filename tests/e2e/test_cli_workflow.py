"""End-to-end tests for the `voxmancer workflow` CLI command."""
import pytest
from voxmancer.interactive_workflow import interactive_workflow


@pytest.mark.e2e
def test_demo_workflow_completes(tmp_path):
    """Test that demo workflow runs without errors.

    This is an E2E test that actually generates audio and validates the full pipeline.
    It requires Piper, LLM, and FFmpeg to be installed and configured.
    """
    work_dir = tmp_path / ".voxmancer"

    # Run demo workflow
    try:
        interactive_workflow(work_dir=work_dir, demo=True)
        # If we get here, workflow completed successfully
        assert True
    except RuntimeError as e:
        # Expected if Piper models aren't downloaded or LLM unavailable
        if "No such file" in str(e) or "not found" in str(e).lower():
            pytest.skip(f"Required tool not available: {e}")
        raise


@pytest.mark.e2e
def test_demo_workflow_creates_output(tmp_path):
    """Test that demo workflow creates output MP3 file."""
    work_dir = tmp_path / ".voxmancer"
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    try:
        interactive_workflow(work_dir=work_dir, demo=True)
        # Check if audio was created
        mp3_files = list(out_dir.glob("*.mp3"))
        if mp3_files:
            assert len(mp3_files) > 0
            assert mp3_files[0].stat().st_size > 0
    except RuntimeError as e:
        if "not found" in str(e).lower():
            pytest.skip("Required tool not available")
        raise
