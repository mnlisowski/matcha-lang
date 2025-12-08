import unittest
import io
from src.reader import CharReader, EOF
from src.position import Position


class TestCharReader(unittest.TestCase):
    def get_reader(self, text):
        return CharReader(io.StringIO(text))

    def test_positions_and_line_counting(self):
        """
        Sprawdza, czy Reader poprawnie wylicza koncową pozycję
        """
        cases = [
            ("empty", "", 1, 1),
            ("one_char", "a", 1, 2),
            ("simple_line", "abc", 1, 4),
            ("ab", "ab", 1, 3),
            ("newline", "a\nb", 2, 2),
            ("only_enter", "\n", 2, 1),
            ("multi_lines", "ab\ncd\ne", 3, 2),
            ("tabulators", "\t\t", 1, 3),
            ("multi_new_lines", "\n\n\n\na\n\naab", 7, 4),
        ]

        for name, text, exp_line, exp_col in cases:
            with self.subTest(case=name):
                reader = self.get_reader(text)

                while reader.current() != EOF:
                    reader.advance()

                self.assertEqual(reader.line, exp_line, f"Błąd linii w '{name}'")
                self.assertEqual(reader.col, exp_col, f"Błąd kolumny w '{name}'")

    def test_full_content_reading(self):
        """
        Sprawdza, czy Reader odczytuje poprawną sekwencję znaków.
        """

        cases = [
            ("empty", "", [EOF]),
            ("simple", "abc", ["a", "b", "c", EOF]),
            ("newlines", "a\nb", ["a", "\n", "b", EOF]),
            (
                "polish",
                "ąź",
                ["ą", "ź", EOF],
            ),  
        ]

        for name, text, expected_chars in cases:
            with self.subTest(case=name):
                reader = self.get_reader(text)
                result_chars = []

                while reader.current() != EOF:
                    result_chars.append(reader.current())
                    reader.advance()

                result_chars.append(EOF)
                self.assertEqual(result_chars, expected_chars)

    def test_check_next_logic(self):
        """
        Testuje logikę podglądu (check_next) na różnych przypadkach.
        """
        cases = [
            # text, current_char_index, expected_next
            ("ab", "b"),
            ("a", EOF),
            ("", EOF),
        ]

        for text, expected_next in cases:
            with self.subTest(text=text):
                reader = self.get_reader(text)

                self.assertEqual(reader.check_next(), expected_next)


if __name__ == "__main__":
    unittest.main()
