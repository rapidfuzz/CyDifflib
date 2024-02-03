from __future__ import annotations

import doctest
import os
import sys
import unittest

import cydifflib


class TestWithAscii(unittest.TestCase):
    def test_one_insert(self):
        sm = cydifflib.SequenceMatcher(None, "b" * 100, "a" + "b" * 100)
        self.assertAlmostEqual(sm.ratio(), 0.995, places=3)
        self.assertEqual(list(sm.get_opcodes()), [("insert", 0, 0, 0, 1), ("equal", 0, 100, 1, 101)])
        self.assertEqual(sm.bpopular, set())
        sm = cydifflib.SequenceMatcher(None, "b" * 100, "b" * 50 + "a" + "b" * 50)
        self.assertAlmostEqual(sm.ratio(), 0.995, places=3)
        self.assertEqual(
            list(sm.get_opcodes()), [("equal", 0, 50, 0, 50), ("insert", 50, 50, 50, 51), ("equal", 50, 100, 51, 101)]
        )
        self.assertEqual(sm.bpopular, set())

    def test_one_delete(self):
        sm = cydifflib.SequenceMatcher(None, "a" * 40 + "c" + "b" * 40, "a" * 40 + "b" * 40)
        self.assertAlmostEqual(sm.ratio(), 0.994, places=3)
        self.assertEqual(
            list(sm.get_opcodes()), [("equal", 0, 40, 0, 40), ("delete", 40, 41, 40, 40), ("equal", 41, 81, 40, 80)]
        )

    def test_bjunk(self):
        sm = cydifflib.SequenceMatcher(isjunk=lambda x: x == " ", a="a" * 40 + "b" * 40, b="a" * 44 + "b" * 40)
        self.assertEqual(sm.bjunk, set())

        sm = cydifflib.SequenceMatcher(
            isjunk=lambda x: x == " ", a="a" * 40 + "b" * 40, b="a" * 44 + "b" * 40 + " " * 20
        )
        self.assertEqual(sm.bjunk, {" "})

        sm = cydifflib.SequenceMatcher(
            isjunk=lambda x: x in [" ", "b"], a="a" * 40 + "b" * 40, b="a" * 44 + "b" * 40 + " " * 20
        )
        self.assertEqual(sm.bjunk, {" ", "b"})


class TestAutojunk(unittest.TestCase):
    """Tests for the autojunk parameter added in 2.7"""

    def test_one_insert_homogenous_sequence(self):
        # By default autojunk=True and the heuristic kicks in for a sequence
        # of length 200+
        seq1 = "b" * 200
        seq2 = "a" + "b" * 200

        sm = cydifflib.SequenceMatcher(None, seq1, seq2)
        self.assertAlmostEqual(sm.ratio(), 0, places=3)
        self.assertEqual(sm.bpopular, {"b"})

        # Now turn the heuristic off
        sm = cydifflib.SequenceMatcher(None, seq1, seq2, autojunk=False)
        self.assertAlmostEqual(sm.ratio(), 0.9975, places=3)
        self.assertEqual(sm.bpopular, set())


class TestSFbugs(unittest.TestCase):
    def test_ratio_for_null_seqn(self):
        # Check clearing of SF bug 763023
        s = cydifflib.SequenceMatcher(None, [], [])
        self.assertEqual(s.ratio(), 1)
        self.assertEqual(s.quick_ratio(), 1)
        self.assertEqual(s.real_quick_ratio(), 1)

    def test_comparing_empty_lists(self):
        # Check fix for bug #979794
        group_gen = cydifflib.SequenceMatcher(None, [], []).get_grouped_opcodes()
        self.assertRaises(StopIteration, next, group_gen)
        diff_gen = cydifflib.unified_diff([], [])
        self.assertRaises(StopIteration, next, diff_gen)

    def test_matching_blocks_cache(self):
        # Issue #21635
        s = cydifflib.SequenceMatcher(None, "abxcd", "abcd")
        first = s.get_matching_blocks()
        self.assertEqual(first[0].size, 2)
        self.assertEqual(first[1].size, 2)
        self.assertEqual(first[2].size, 0)
        second = s.get_matching_blocks()
        self.assertEqual(second[0].size, 2)
        self.assertEqual(second[1].size, 2)
        self.assertEqual(second[2].size, 0)

    def test_added_tab_hint(self):
        # Check fix for bug #1488943
        diff = list(cydifflib.Differ().compare(["\tI am a buggy"], ["\t\tI am a bug"]))
        self.assertEqual("- \tI am a buggy", diff[0])
        self.assertEqual("? \t          --\n", diff[1])
        self.assertEqual("+ \t\tI am a bug", diff[2])
        self.assertEqual("? +\n", diff[3])

    def test_hint_indented_properly_with_tabs(self):
        diff = list(cydifflib.Differ().compare(["\t \t \t^"], ["\t \t \t^\n"]))
        self.assertEqual("- \t \t \t^", diff[0])
        self.assertEqual("+ \t \t \t^\n", diff[1])
        self.assertEqual("? \t \t \t +\n", diff[2])

    # def test_mdiff_catch_stop_iteration(self):
    #    # Issue #33224
    #    self.assertEqual(
    #        list(cydifflib._mdiff(["2"], ["3"], 1)),
    #        [((1, '\x00-2\x01'), (1, '\x00+3\x01'), True)],
    #    )

    def test_issue3(self):
        a = "计算:[小题]根号81+-273+-3分之22;[小题]-273+根号9-4分之1×根号0.16."
        b = "已知3x+1的算术平方根是4,x+2y的立方根是-1,(1)求x、y的值；(2)求2x-5y的平方根."
        self.assertEqual(cydifflib.SequenceMatcher(None, a, b).ratio(), 0.12)


patch914575_from1 = """
   1. Beautiful is beTTer than ugly.
   2. Explicit is better than implicit.
   3. Simple is better than complex.
   4. Complex is better than complicated.
"""

patch914575_to1 = """
   1. Beautiful is better than ugly.
   3.   Simple is better than complex.
   4. Complicated is better than complex.
   5. Flat is better than nested.
"""

patch914575_nonascii_from1 = """
   1. Beautiful is beTTer than ugly.
   2. Explicit is better than ımplıcıt.
   3. Simple is better than complex.
   4. Complex is better than complicated.
"""

patch914575_nonascii_to1 = """
   1. Beautiful is better than ügly.
   3.   Sımple is better than complex.
   4. Complicated is better than cömplex.
   5. Flat is better than nested.
"""

patch914575_from2 = """
\t\tLine 1: preceded by from:[tt] to:[ssss]
  \t\tLine 2: preceded by from:[sstt] to:[sssst]
  \t \tLine 3: preceded by from:[sstst] to:[ssssss]
Line 4:  \thas from:[sst] to:[sss] after :
Line 5: has from:[t] to:[ss] at end\t
"""

patch914575_to2 = """
    Line 1: preceded by from:[tt] to:[ssss]
    \tLine 2: preceded by from:[sstt] to:[sssst]
      Line 3: preceded by from:[sstst] to:[ssssss]
Line 4:   has from:[sst] to:[sss] after :
Line 5: has from:[t] to:[ss] at end
"""

patch914575_from3 = """line 0
1234567890123456789012345689012345
line 1
line 2
line 3
line 4   changed
line 5   changed
line 6   changed
line 7
line 8  subtracted
line 9
1234567890123456789012345689012345
short line
just fits in!!
just fits in two lines yup!!
the end"""

patch914575_to3 = """line 0
1234567890123456789012345689012345
line 1
line 2    added
line 3
line 4   chanGEd
line 5a  chanGed
line 6a  changEd
line 7
line 8
line 9
1234567890
another long line that needs to be wrapped
just fitS in!!
just fits in two lineS yup!!
the end"""


class TestSFpatches(unittest.TestCase):
    def test_html_diff(self):
        # Check SF patch 914575 for generating HTML differences
        f1a = (patch914575_from1 + "123\n" * 10) * 3
        t1a = (patch914575_to1 + "123\n" * 10) * 3
        f1b = "456\n" * 10 + f1a
        t1b = "456\n" * 10 + t1a
        f1a = f1a.splitlines()
        t1a = t1a.splitlines()
        f1b = f1b.splitlines()
        t1b = t1b.splitlines()
        f2 = patch914575_from2.splitlines()
        t2 = patch914575_to2.splitlines()
        f3 = patch914575_from3
        t3 = patch914575_to3
        i = cydifflib.HtmlDiff()
        j = cydifflib.HtmlDiff(tabsize=2)
        k = cydifflib.HtmlDiff(wrapcolumn=14)

        full = i.make_file(f1a, t1a, "from", "to", context=False, numlines=5)
        tables = "\n".join(
            [
                "<h2>Context (first diff within numlines=5(default))</h2>",
                i.make_table(f1a, t1a, "from", "to", context=True),
                "<h2>Context (first diff after numlines=5(default))</h2>",
                i.make_table(f1b, t1b, "from", "to", context=True),
                "<h2>Context (numlines=6)</h2>",
                i.make_table(f1a, t1a, "from", "to", context=True, numlines=6),
                "<h2>Context (numlines=0)</h2>",
                i.make_table(f1a, t1a, "from", "to", context=True, numlines=0),
                "<h2>Same Context</h2>",
                i.make_table(f1a, f1a, "from", "to", context=True),
                "<h2>Same Full</h2>",
                i.make_table(f1a, f1a, "from", "to", context=False),
                "<h2>Empty Context</h2>",
                i.make_table([], [], "from", "to", context=True),
                "<h2>Empty Full</h2>",
                i.make_table([], [], "from", "to", context=False),
                "<h2>tabsize=2</h2>",
                j.make_table(f2, t2),
                "<h2>tabsize=default</h2>",
                i.make_table(f2, t2),
                "<h2>Context (wrapcolumn=14,numlines=0)</h2>",
                k.make_table(f3.splitlines(), t3.splitlines(), context=True, numlines=0),
                "<h2>wrapcolumn=14,splitlines()</h2>",
                k.make_table(f3.splitlines(), t3.splitlines()),
                "<h2>wrapcolumn=14,splitlines(True)</h2>",
                k.make_table(f3.splitlines(True), t3.splitlines(True)),
            ]
        )
        actual = full.replace("</body>", "\n%s\n</body>" % tables)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "test_cydifflib_expect.html")
        # temporarily uncomment next two lines to baseline this test
        # with open(file_path,'w') as fp:
        #    fp.write(actual)

        with open(file_path, encoding="utf-8") as fp:
            self.assertEqual(actual, fp.read())

    def test_recursion_limit(self):
        # Check if the problem described in patch #1413711 exists.
        limit = sys.getrecursionlimit()
        old = [(i % 2 and "K:%d" or "V:A:%d") % i for i in range(limit * 2)]
        new = [(i % 2 and "K:%d" or "V:B:%d") % i for i in range(limit * 2)]
        cydifflib.SequenceMatcher(None, old, new).get_opcodes()

    def test_make_file_default_charset(self):
        html_diff = cydifflib.HtmlDiff()
        output = html_diff.make_file(patch914575_from1.splitlines(), patch914575_to1.splitlines())
        self.assertIn('content="text/html; charset=utf-8"', output)

    def test_make_file_iso88591_charset(self):
        html_diff = cydifflib.HtmlDiff()
        output = html_diff.make_file(patch914575_from1.splitlines(), patch914575_to1.splitlines(), charset="iso-8859-1")
        self.assertIn('content="text/html; charset=iso-8859-1"', output)

    def test_make_file_usascii_charset_with_nonascii_input(self):
        html_diff = cydifflib.HtmlDiff()
        output = html_diff.make_file(
            patch914575_nonascii_from1.splitlines(), patch914575_nonascii_to1.splitlines(), charset="us-ascii"
        )
        self.assertIn('content="text/html; charset=us-ascii"', output)
        self.assertIn("&#305;mpl&#305;c&#305;t", output)


class TestOutputFormat(unittest.TestCase):
    def test_tab_delimiter(self):
        args = ["one", "two", "Original", "Current", "2005-01-26 23:30:50", "2010-04-02 10:20:52"]
        ud = cydifflib.unified_diff(*args, lineterm="")
        self.assertEqual(list(ud)[0:2], ["--- Original\t2005-01-26 23:30:50", "+++ Current\t2010-04-02 10:20:52"])
        cd = cydifflib.context_diff(*args, lineterm="")
        self.assertEqual(list(cd)[0:2], ["*** Original\t2005-01-26 23:30:50", "--- Current\t2010-04-02 10:20:52"])

    def test_no_trailing_tab_on_empty_filedate(self):
        args = ["one", "two", "Original", "Current"]
        ud = cydifflib.unified_diff(*args, lineterm="")
        self.assertEqual(list(ud)[0:2], ["--- Original", "+++ Current"])

        cd = cydifflib.context_diff(*args, lineterm="")
        self.assertEqual(list(cd)[0:2], ["*** Original", "--- Current"])

    # def test_range_format_unified(self):
    #    # Per the diff spec at http://www.unix.org/single_unix_specification/
    #    spec = '''\
    #       Each <range> field shall be of the form:
    #         %1d", <beginning line number>  if the range contains exactly one line,
    #       and:
    #        "%1d,%1d", <beginning line number>, <number of lines> otherwise.
    #       If a range is empty, its beginning line number shall be the number of
    #       the line just before the range, or 0 if the empty range starts the file.
    #    '''
    #    fmt = cydifflib._format_range_unified
    #    self.assertEqual(fmt(3,3), '3,0')
    #    self.assertEqual(fmt(3,4), '4')
    #    self.assertEqual(fmt(3,5), '4,2')
    #    self.assertEqual(fmt(3,6), '4,3')
    #    self.assertEqual(fmt(0,0), '0,0')

    # def test_range_format_context(self):
    #    # Per the diff spec at http://www.unix.org/single_unix_specification/
    #    spec = '''\
    #       The range of lines in file1 shall be written in the following format
    #       if the range contains two or more lines:
    #           "*** %d,%d ****\n", <beginning line number>, <ending line number>
    #       and the following format otherwise:
    #           "*** %d ****\n", <ending line number>
    #       The ending line number of an empty range shall be the number of the preceding line,
    #       or 0 if the range is at the start of the file.
    #
    #       Next, the range of lines in file2 shall be written in the following format
    #       if the range contains two or more lines:
    #           "--- %d,%d ----\n", <beginning line number>, <ending line number>
    #       and the following format otherwise:
    #           "--- %d ----\n", <ending line number>
    #    '''
    #    fmt = cydifflib._format_range_context
    #    self.assertEqual(fmt(3,3), '3')
    #    self.assertEqual(fmt(3,4), '4')
    #    self.assertEqual(fmt(3,5), '4,5')
    #    self.assertEqual(fmt(3,6), '4,6')
    #    self.assertEqual(fmt(0,0), '0')


class TestBytes(unittest.TestCase):
    # don't really care about the content of the output, just the fact
    # that it's bytes and we don't crash
    def check(self, diff):
        diff = list(diff)  # trigger exceptions first
        for line in diff:
            self.assertIsInstance(line, bytes, "all lines of diff should be bytes, but got: %r" % line)

    def test_byte_content(self):
        # if we receive byte strings, we return byte strings
        a = [b"hello", b"andr\xe9"]  # iso-8859-1 bytes
        b = [b"hello", b"andr\xc3\xa9"]  # utf-8 bytes

        unified = cydifflib.unified_diff
        context = cydifflib.context_diff

        check = self.check
        check(cydifflib.diff_bytes(unified, a, a))
        check(cydifflib.diff_bytes(unified, a, b))

        # now with filenames (content and filenames are all bytes!)
        check(cydifflib.diff_bytes(unified, a, a, b"a", b"a"))
        check(cydifflib.diff_bytes(unified, a, b, b"a", b"b"))

        # and with filenames and dates
        check(cydifflib.diff_bytes(unified, a, a, b"a", b"a", b"2005", b"2013"))
        check(cydifflib.diff_bytes(unified, a, b, b"a", b"b", b"2005", b"2013"))

        # same all over again, with context diff
        check(cydifflib.diff_bytes(context, a, a))
        check(cydifflib.diff_bytes(context, a, b))
        check(cydifflib.diff_bytes(context, a, a, b"a", b"a"))
        check(cydifflib.diff_bytes(context, a, b, b"a", b"b"))
        check(cydifflib.diff_bytes(context, a, a, b"a", b"a", b"2005", b"2013"))
        check(cydifflib.diff_bytes(context, a, b, b"a", b"b", b"2005", b"2013"))

    def test_byte_filenames(self):
        # somebody renamed a file from ISO-8859-2 to UTF-8
        fna = b"\xb3odz.txt"  # "łodz.txt"
        fnb = b"\xc5\x82odz.txt"

        # they transcoded the content at the same time
        a = [b"\xa3odz is a city in Poland."]
        b = [b"\xc5\x81odz is a city in Poland."]

        check = self.check
        unified = cydifflib.unified_diff
        context = cydifflib.context_diff
        check(cydifflib.diff_bytes(unified, a, b, fna, fnb))
        check(cydifflib.diff_bytes(context, a, b, fna, fnb))

        def assertDiff(expect, actual):
            # do not compare expect and equal as lists, because unittest
            # uses cydifflib to report difference between lists
            actual = list(actual)
            self.assertEqual(len(expect), len(actual))
            for e, a in zip(expect, actual):
                self.assertEqual(e, a)

        expect = [
            b"--- \xb3odz.txt",
            b"+++ \xc5\x82odz.txt",
            b"@@ -1 +1 @@",
            b"-\xa3odz is a city in Poland.",
            b"+\xc5\x81odz is a city in Poland.",
        ]
        actual = cydifflib.diff_bytes(unified, a, b, fna, fnb, lineterm=b"")
        assertDiff(expect, actual)

        # with dates (plain ASCII)
        datea = b"2005-03-18"
        dateb = b"2005-03-19"
        check(cydifflib.diff_bytes(unified, a, b, fna, fnb, datea, dateb))
        check(cydifflib.diff_bytes(context, a, b, fna, fnb, datea, dateb))

        expect = [
            # note the mixed encodings here: this is deeply wrong by every
            # tenet of Unicode, but it doesn't crash, it's parseable by
            # patch, and it's how UNIX(tm) diff behaves
            b"--- \xb3odz.txt\t2005-03-18",
            b"+++ \xc5\x82odz.txt\t2005-03-19",
            b"@@ -1 +1 @@",
            b"-\xa3odz is a city in Poland.",
            b"+\xc5\x81odz is a city in Poland.",
        ]
        actual = cydifflib.diff_bytes(unified, a, b, fna, fnb, datea, dateb, lineterm=b"")
        assertDiff(expect, actual)

    def test_mixed_types_content(self):
        # type of input content must be consistent: all str or all bytes
        a = [b"hello"]
        b = ["hello"]

        unified = cydifflib.unified_diff
        context = cydifflib.context_diff

        expect = "lines to compare must be str, not bytes (b'hello')"
        self._assert_type_error(expect, unified, a, b)
        self._assert_type_error(expect, unified, b, a)
        self._assert_type_error(expect, context, a, b)
        self._assert_type_error(expect, context, b, a)

        expect = "all arguments must be bytes, not str ('hello')"
        self._assert_type_error(expect, cydifflib.diff_bytes, unified, a, b)
        self._assert_type_error(expect, cydifflib.diff_bytes, unified, b, a)
        self._assert_type_error(expect, cydifflib.diff_bytes, context, a, b)
        self._assert_type_error(expect, cydifflib.diff_bytes, context, b, a)

    def test_mixed_types_filenames(self):
        # cannot pass filenames as bytes if content is str (this may not be
        # the right behaviour, but at least the test demonstrates how
        # things work)
        a = ["hello\n"]
        b = ["ohell\n"]
        fna = b"ol\xe9.txt"  # filename transcoded from ISO-8859-1
        fnb = b"ol\xc3a9.txt"  # to UTF-8
        self._assert_type_error(
            "all arguments must be str, not: b'ol\\xe9.txt'", cydifflib.unified_diff, a, b, fna, fnb
        )

    def test_mixed_types_dates(self):
        # type of dates must be consistent with type of contents
        a = [b"foo\n"]
        b = [b"bar\n"]
        datea = "1 fév"
        dateb = "3 fév"
        self._assert_type_error(
            "all arguments must be bytes, not str ('1 fév')",
            cydifflib.diff_bytes,
            cydifflib.unified_diff,
            a,
            b,
            b"a",
            b"b",
            datea,
            dateb,
        )

        # if input is str, non-ASCII dates are fine
        a = ["foo\n"]
        b = ["bar\n"]
        list(cydifflib.unified_diff(a, b, "a", "b", datea, dateb))

    def _assert_type_error(self, msg, generator, *args):
        with self.assertRaises(TypeError) as ctx:
            list(generator(*args))
        self.assertEqual(msg, str(ctx.exception))


class TestJunkAPIs(unittest.TestCase):
    def test_is_line_junk_true(self):
        for line in ["#", "  ", " #", "# ", " # ", ""]:
            self.assertTrue(cydifflib.IS_LINE_JUNK(line), repr(line))

    def test_is_line_junk_false(self):
        for line in ["##", " ##", "## ", "abc ", "abc #", "Mr. Moose is up!"]:
            self.assertFalse(cydifflib.IS_LINE_JUNK(line), repr(line))

    def test_is_line_junk_REDOS(self):
        evil_input = ("\t" * 1000000) + "##"
        self.assertFalse(cydifflib.IS_LINE_JUNK(evil_input))

    def test_is_character_junk_true(self):
        for char in [" ", "\t"]:
            self.assertTrue(cydifflib.IS_CHARACTER_JUNK(char), repr(char))

    def test_is_character_junk_false(self):
        for char in ["a", "#", "\n", "\f", "\r", "\v"]:
            self.assertFalse(cydifflib.IS_CHARACTER_JUNK(char), repr(char))


class TestFindLongest(unittest.TestCase):
    def longer_match_exists(self, a, b, n):
        return any(b_part in a for b_part in [b[i : i + n + 1] for i in range(len(b) - n - 1)])

    def test_default_args(self):
        a = "foo bar"
        b = "foo baz bar"
        sm = cydifflib.SequenceMatcher(a=a, b=b)
        match = sm.find_longest_match()
        self.assertEqual(match.a, 0)
        self.assertEqual(match.b, 0)
        self.assertEqual(match.size, 6)
        self.assertEqual(a[match.a : match.a + match.size], b[match.b : match.b + match.size])
        self.assertFalse(self.longer_match_exists(a, b, match.size))

        match = sm.find_longest_match(alo=2, blo=4)
        self.assertEqual(match.a, 3)
        self.assertEqual(match.b, 7)
        self.assertEqual(match.size, 4)
        self.assertEqual(a[match.a : match.a + match.size], b[match.b : match.b + match.size])
        self.assertFalse(self.longer_match_exists(a[2:], b[4:], match.size))

        match = sm.find_longest_match(bhi=5, blo=1)
        self.assertEqual(match.a, 1)
        self.assertEqual(match.b, 1)
        self.assertEqual(match.size, 4)
        self.assertEqual(a[match.a : match.a + match.size], b[match.b : match.b + match.size])
        self.assertFalse(self.longer_match_exists(a, b[1:5], match.size))

    def test_longest_match_with_popular_chars(self):
        a = "dabcd"
        b = "d" * 100 + "abc" + "d" * 100  # length over 200 so popular used
        sm = cydifflib.SequenceMatcher(a=a, b=b)
        match = sm.find_longest_match(0, len(a), 0, len(b))
        self.assertEqual(match.a, 0)
        self.assertEqual(match.b, 99)
        self.assertEqual(match.size, 5)
        self.assertEqual(a[match.a : match.a + match.size], b[match.b : match.b + match.size])
        self.assertFalse(self.longer_match_exists(a, b, match.size))


def setUpModule():
    cydifflib.HtmlDiff._default_prefix = 0


def load_tests(loader, tests, pattern):
    tests.addTest(doctest.DocTestSuite(cydifflib))
    return tests


if __name__ == "__main__":
    unittest.main()
