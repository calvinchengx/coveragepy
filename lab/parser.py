"""Parser.py: a main for invoking code in coverage/parser.py"""

import glob, os, sys
from optparse import OptionParser

import disgen

from coverage.misc import CoverageException
from coverage.parser import ByteParser, CodeParser


class ParserMain(object):
    """A main for code parsing experiments."""

    def main(self, args):
        """A main function for trying the code from the command line."""

        parser = OptionParser()
        parser.add_option(
            "-c", action="store_true", dest="chunks",
            help="Show basic block chunks"
            )
        parser.add_option(
            "-d", action="store_true", dest="dis",
            help="Disassemble"
            )
        parser.add_option(
            "-R", action="store_true", dest="recursive",
            help="Recurse to find source files"
            )
        parser.add_option(
            "-s", action="store_true", dest="source",
            help="Show analyzed source"
            )
        parser.add_option(
            "-t", action="store_true", dest="tokens",
            help="Show tokens"
            )

        options, args = parser.parse_args()
        if options.recursive:
            if args:
                root = args[0]
            else:
                root = "."
            for root, _, _ in os.walk(root):
                for f in glob.glob(root + "/*.py"):
                    self.one_file(options, f)
        elif not args:
            parser.print_help()
        else:
            self.one_file(options, args[0])

    def one_file(self, options, filename):
        """Process just one file."""

        if options.dis or options.chunks:
            try:
                bp = ByteParser(filename=filename)
            except CoverageException:
                _, err, _ = sys.exc_info()
                print("%s" % (err,))
                return

        if options.dis:
            print("Main code:")
            self.disassemble(bp)

        if options.chunks:
            chunks = bp._all_chunks()
            if options.recursive:
                print("%6d: %s" % (len(chunks), filename))
            else:
                print("Chunks: %r" % chunks)
                arcs = bp._all_arcs()
                print("Arcs: %r" % sorted(arcs))

        if options.source or options.tokens:
            cp = CodeParser(filename=filename, exclude=r"no\s*cover")
            cp.show_tokens = options.tokens
            cp._raw_parse()

            if options.source:
                if options.chunks:
                    arc_width, arc_chars = self.arc_ascii_art(arcs)
                else:
                    arc_width, arc_chars = 0, {}

                exit_counts = cp.exit_counts()

                for i, ltext in enumerate(cp.lines):
                    lineno = i+1
                    m0 = m1 = m2 = m3 = a = ' '
                    if lineno in cp.statement_starts:
                        m0 = '-'
                    exits = exit_counts.get(lineno, 0)
                    if exits > 1:
                        m1 = str(exits)
                    if lineno in cp.docstrings:
                        m2 = '"'
                    if lineno in cp.classdefs:
                        m2 = 'C'
                    if lineno in cp.excluded:
                        m3 = 'x'
                    a = arc_chars.get(lineno, '').ljust(arc_width)
                    print("%4d %s%s%s%s%s %s" %
                                (lineno, m0, m1, m2, m3, a, ltext)
                        )

    def disassemble(self, byte_parser):
        """Disassemble code, for ad-hoc experimenting."""

        for bp in byte_parser.child_parsers():
            chunks = bp._split_into_chunks()
            chunkd = dict((chunk.byte, chunk) for chunk in chunks)
            if bp.text:
                srclines = bp.text.splitlines()
            else:
                srclines = None
            print("\n%s: " % bp.code)
            for disline in disgen.disgen(bp.code):
                if disline.first:
                    if srclines:
                        print("%80s%s" % ("", srclines[disline.lineno-1]))
                    elif disline.offset > 0:
                        print("")
                line = disgen.format_dis_line(disline)
                chunk = chunkd.get(disline.offset)
                if chunk:
                    exits = " ".join(str(e) for e in sorted(chunk.exits))
                    chunkstr = ": %s" % exits
                else:
                    chunkstr = ""
                print("%-70s%s" % (line, chunkstr))

        print("")

    def arc_ascii_art(self, arcs):
        """Draw arcs as ascii art.

        Returns a width of characters needed to draw all the arcs, and a
        dictionary mapping line numbers to ascii strings to draw for that line.

        """
        arc_chars = {}
        for lfrom, lto in sorted(arcs):
            if lfrom < 0:
                arc_chars[lto] = arc_chars.get(lto, '') + 'v'
            elif lto < 0:
                arc_chars[lfrom] = arc_chars.get(lfrom, '') + '^'
            else:
                if lfrom == lto - 1:
                    # Don't show obvious arcs.
                    continue
                if lfrom < lto:
                    l1, l2 = lfrom, lto
                else:
                    l1, l2 = lto, lfrom
                w = max([len(arc_chars.get(l, '')) for l in range(l1, l2+1)])
                for l in range(l1, l2+1):
                    if l == lfrom:
                        ch = '<'
                    elif l == lto:
                        ch = '>'
                    else:
                        ch = '|'
                    arc_chars[l] = arc_chars.get(l, '').ljust(w) + ch
                arc_width = 0

        if arc_chars:
            arc_width = max([len(a) for a in arc_chars.values()])
        else:
            arc_width = 0

        return arc_width, arc_chars

if __name__ == '__main__':
    ParserMain().main(sys.argv[1:])

