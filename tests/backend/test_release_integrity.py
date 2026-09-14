import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from concnshare.config import ClipConfig
from datahub.workers.clip import build


class ReleaseIntegrityTests(unittest.TestCase):
    def test_changed_boundary_or_converter_cannot_produce_published_result(self):
        for change in ('boundary', 'converter'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                cfg = ClipConfig(input_pfb_dir=root, shp_dir=root, tif_dir=root,
                                 pfmask_cmd=root / 'converter.exe')
                files = []
                for name in cfg.pfb_inputs:
                    (root / name).write_bytes(b'known-source')
                    files.append(dict(file_kind='source', storage_key=name,
                                      source_sha256=hashlib.sha256(b'known-source').hexdigest()))
                (root / 'PFBAS12.shp').write_bytes(b'changed' if change == 'boundary' else b'boundary')
                cfg.pfmask_cmd.write_bytes(b'changed' if change == 'converter' else b'converter')
                grid = dict(source_assets=[dict(kind='shp', name='PFBAS12.shp',
                                               sha256=hashlib.sha256(b'boundary').hexdigest())],
                            pfmask_sha256=hashlib.sha256(b'converter').hexdigest())
                snapshot = dict(files=files, grid=grid, pfbas_level=12)
                with patch('datahub.workers.clip.ClipConfig', return_value=cfg), \
                     patch('datahub.workers.clip.run_basin_clip') as clip:
                    with self.assertRaises(ValueError):
                        build(snapshot, root)
                    clip.assert_not_called()
                self.assertFalse((root / 'result.zip').exists())
