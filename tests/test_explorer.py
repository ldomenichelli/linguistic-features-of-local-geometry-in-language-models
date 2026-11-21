"""Regression checks for joins and paper transcription edge cases."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_site import check_data, check_results, check_progressive
from import_current_paper import table_rows


class ExplorerIntegrity(unittest.TestCase):
    def test_entire_release_matches_measurements(self):
        check_data()

    def test_progressive_chunks_preserve_source_precision_and_cohort(self):
        check_progressive()

    def test_current_and_archived_downloads_match_sources(self):
        check_results()

    def test_spanning_headers_and_extended_table_preamble(self):
        # Real LaTeX edge cases: width argument, nested preamble, grouped headers,
        # carried model labels, and an escaped ampersand inside a text cell.
        tex = r'''\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcc@{}}
\toprule Model & \multicolumn{2}{c}{Scores} \\
\multirow{2}{*}{Model A} & .5 & .6 \\
 & .7 & A\&B \\
\bottomrule\end{tabular*}'''
        rows, spans = table_rows(tex, 'tabular*')
        self.assertEqual(rows, [['Model', 'Scores'], ['Model A', '.5', '.6'], ['Model A', '.7', 'A&B']])
        self.assertEqual(spans[0], [1, 2])
