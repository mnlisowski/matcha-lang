import unittest
from src.reader import CharReader, EOF


class TestCharReader(unittest.TestCase):
    def test_empty_source(self):
        # Pusty plik
        reader = CharReader("")

        self.assertEqual(reader.current(), EOF)
        self.assertEqual(reader.advance(), EOF)

    def test_code_snippet(self):
        code = """fun main() {
        var x = 10;
}"""
        reader = CharReader(code)

        self.assertEqual(reader.current(), "f")
        self.assertEqual(str(reader.position()), "[1:1]")

        reader.advance()
        reader.advance()

        char = reader.advance()
        self.assertEqual(char, " ")
        self.assertEqual(str(reader.position()), "[1:4]")

    def test_line_counting(self):
        source = "A\nB\nC"
        reader = CharReader(source)

        self.assertEqual(reader.current(), "A")
        self.assertEqual(str(reader.position()), "[1:1]")

        char = reader.advance()
        self.assertEqual(char, "\n")

        char = reader.advance()
        self.assertEqual(char, "B")
        self.assertEqual(str(reader.position()), "[2:1]")

        reader.advance()

        char = reader.advance()
        self.assertEqual(char, "C")
        self.assertEqual(str(reader.position()), "[3:1]")

    def test_eof_behavior(self):
        reader = CharReader("a")

        reader.advance()
        self.assertEqual(reader.current(), EOF)

        self.assertEqual(reader.advance(), EOF)
        self.assertEqual(reader.advance(), EOF)

        self.assertEqual(reader.check_next(), EOF)

    def test_unicode_chars(self):
        reader = CharReader("Zażółć")

        self.assertEqual(reader.current(), "Z")
        self.assertEqual(str(reader.position()), "[1:1]")

        reader.advance()
        reader.advance()

        self.assertEqual(reader.current(), "ż")
        self.assertEqual(str(reader.position()), "[1:3]")


if __name__ == "__main__":
    unittest.main()
