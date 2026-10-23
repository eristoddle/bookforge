import os
import tempfile

# Settings are read when bookforge is imported, so point storage at a scratch folder first.
_scratch = tempfile.mkdtemp(prefix="bookforge-test-")
os.environ.setdefault("TEMP_DIR", os.path.join(_scratch, "temp"))
os.environ.setdefault("OUTPUT_DIR", os.path.join(_scratch, "out"))
