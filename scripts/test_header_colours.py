"""Regression check: an admin header change reaches every generated card record."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cases

ROOT = Path(__file__).resolve().parent.parent


class HeaderColourPropagation(unittest.TestCase):
    def test_admin_palette_round_trip(self):
        record = json.loads((ROOT / 'content/cases/aiid.json').read_text())
        for background in ('accent', '#EEF1FA', '#FBEAE8', '#F2F2F5'):
            with self.subTest(background=background), tempfile.TemporaryDirectory() as temp:
                temp = Path(temp)
                paths = {}
                for name, filename in [('MAIN', 'Main'), ('DUST', 'Dust'),
                                       ('TIMELINE', 'Timeline'), ('CONNECTIONS', 'Connections')]:
                    target = temp / (filename + '.dc.html')
                    target.write_text((ROOT / 'project' / target.name).read_text())
                    paths[name] = str(target)
                changed = copy.deepcopy(record)
                changed['header']['background'] = background
                with patch.multiple(cases, **paths):
                    cases.write_cards({'aiid': changed})
                # Test the actual records consumed by search, thematic cards and Dust.
                for name in ('MAIN', 'DUST'):
                    _, _, lines = cases.item_lines(Path(paths[name]).read_text())
                    aiid = next(line for line in lines if line.startswith("{ id: 'aiid'"))
                    self.assertIn("headerBackground: " + cases.js(background), aiid)
                timeline = Path(paths['TIMELINE']).read_text()
                import re
                companies = json.loads(re.search(r'var COMPANIES = (\[.*?\]);\n', timeline, re.S)[1])
                projects = [p for c in companies for p in c.get('projects', []) if p['id'] == 'aiid']
                self.assertTrue(projects)
                self.assertTrue(all(p['headerBackground'] == background for p in projects))
                # The case-study header uses the same choice, with white type on solid blue.
                page = cases.render(changed)
                paint = '{{accent}}' if background == 'accent' else background
                ink = '#FFFFFF' if background == 'accent' else '#17171F'
                self.assertIn('background: %s; color: %s' % (paint, ink), page)


if __name__ == '__main__':
    unittest.main()
