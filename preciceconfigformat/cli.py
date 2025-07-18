#! /usr/bin/env python3

from lxml import etree
import itertools
import argparse
import sys
import io
import shutil


def isEmptyTag(element):
    return not element.getchildren()


def isComment(element):
    return isinstance(element, etree._Comment)


def attribLength(element):
    total = 0
    for k, v in element.items():
        # KEY="VALUE"
        total += len(k) + 2 + len(v) + 1
    # spaces in between
    total += len(element.attrib) - 1
    return total


def elementLen(element):
    total = 2  # Open close
    total += len(element.tag)
    if element.attrib:
        total += 1 + attribLength(element)
    if isEmptyTag(element):
        total += 2  # space and slash
    return total


class PrettyPrinter:
    def __init__(self, stream=sys.stdout, indent="  ", maxwidth=100, maxgrouplevel=1):
        self.stream = stream
        self.indent = indent
        self.maxwidth = maxwidth
        self.maxgrouplevel = maxgrouplevel

    def print(self, text=""):
        self.stream.write(text + "\n")

    def fmtAttrH(self, element):
        return " ".join(['{}="{}"'.format(k, v) for k, v in element.items()])

    def fmtAttrV(self, element, level):
        prefix = self.indent * (level + 1)
        return "\n".join(['{}{}="{}"'.format(prefix, k, v) for k, v in element.items()])

    def printXMLDeclaration(self, root):
        self.print(
            '<?xml version="{}" encoding="{}" ?>'.format(
                root.docinfo.xml_version, root.docinfo.encoding
            )
        )

    def printRoot(self, root):
        self.printXMLDeclaration(root)
        self.printElement(root.getroot(), level=0)

    def printTagStart(self, element, level):
        assert isinstance(element, etree._Element)
        if element.attrib:
            if elementLen(element) + len(self.indent) * level <= self.maxwidth:
                self.print(
                    "{}<{} {}>".format(
                        self.indent * level, element.tag, self.fmtAttrH(element)
                    )
                )
            else:
                self.print("{}<{}".format(self.indent * level, element.tag))
                self.print("{}>".format(self.fmtAttrV(element, level)))
        else:
            self.print("{}<{}>".format(self.indent * level, element.tag))

    def printTagEnd(self, element, level):
        assert isinstance(element, etree._Element)
        self.print("{}</{}>".format(self.indent * level, element.tag))

    def printTagEmpty(self, element, level):
        assert isinstance(element, etree._Element)
        if element.attrib:
            if elementLen(element) + len(self.indent) * level <= self.maxwidth:
                self.print(
                    "{}<{} {} />".format(
                        self.indent * level, element.tag, self.fmtAttrH(element)
                    )
                )
            else:
                self.print("{}<{}".format(self.indent * level, element.tag))
                self.print("{} />".format(self.fmtAttrV(element, level)))
        else:
            self.print("{}<{} />".format(self.indent * level, element.tag))

    def printComment(self, element, level):
        assert isinstance(element, etree._Comment)
        self.print(self.indent * level + str(element))

    def printElement(self, element, level):
        if isinstance(element, etree._Comment):
            self.printComment(element, level=level)
            return

        if isEmptyTag(element):
            self.printTagEmpty(element, level=level)
        else:
            self.printTagStart(element, level=level)
            self.printChildren(element, level=level + 1)
            self.printTagEnd(element, level=level)

    def printChildren(self, element, level):
        if level > self.maxgrouplevel:
            for child in element.getchildren():
                self.printElement(child, level=level)
            return

        groups1 = itertools.groupby(
            element.getchildren(), lambda e: str(e.tag).split(":")[0]
        )

        groups = []

        for _, group in groups1:
            group = list(group)
            if isEmptyTag(group[0]):
                groups.append(group)
            else:
                groups += [[e] for e in group]

        last = len(groups)
        for i, group in enumerate(groups, start=1):
            for child in group:
                self.printElement(child, level=level)
            if not (isComment(group[0]) or (i == last)):
                self.print()


def makeFormatParser(add_help: bool = True):
    parser = argparse.ArgumentParser(
        add_help=add_help,
        description="Consistently format preCICE configuration files.",
    )
    parser.add_argument(
        "files", nargs="+", type=str, help="The XML configuration files."
    )
    return parser


def parse_args():
    parser = makeFormatParser()
    return parser.parse_args()


def parseXML(content):
    p = etree.XMLParser(recover=True, remove_comments=False, remove_blank_text=True)
    return etree.fromstring(content, p).getroottree()


def example():
    return parseXML(open("./BB-sockets-explicit-twoway.xml", "r").read())


def formatFile(filename):
    content = None
    try:
        with open(filename, "rb") as xml_file:
            content = xml_file.read()
    except Exception as e:
        print(f'Unable to open file: "{filename}"')
        print(e)
        return 1

    xml = None
    try:
        xml = parseXML(content)
    except Exception as e:
        print(f'Error occurred while parsing file: "{filename}"')
        print(e)
        return 1

    buffer = io.StringIO()
    printer = PrettyPrinter(stream=buffer)
    printer.printRoot(xml)

    if buffer.getvalue() != content.decode("utf-8"):
        print(f'Reformatting file: "{filename}"')
        with open(filename, "w") as xml_file:
            buffer.seek(0)
            shutil.copyfileobj(buffer, xml_file)
        return 2
    return 0


def formatFiles(files):
    modified = False
    failed = False

    for filename in files:
        ret = formatFile(filename)
        if ret == 1:
            failed = True
        elif ret == 2:
            modified = True

    if failed:
        return 1

    if modified:
        return 2

    return 0


def runFormat(ns):
    return formatFiles(ns.files)


def main():
    args = parse_args()
    return runFormat(args)


if __name__ == "__main__":
    sys.exit(main())
