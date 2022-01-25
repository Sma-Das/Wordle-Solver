"""
A simple Wordle solver designed in python3.10
@author InfernoCheese
"""

from string import ascii_lowercase as lowercase


class Wordlist:
    WORD_SIZE: int = 5

    def __init__(self, filename: str, word_size: int = WORD_SIZE):
        wordlist = self.read_file(filename)
        self.wordlist = self.remove_duplicates(wordlist)
        self.default_filters = [
            lambda w: len(w) == word_size,
            lambda w: all(l in lowercase for l in w),
        ]

    def __iter__(self):
        yield from self.wordlist

    @staticmethod
    def read_file(filename: str) -> list[str]:
        with open(filename, "r") as wordlist:
            return wordlist \
                .read() \
                .rstrip() \
                .split("\n")

    @staticmethod
    def remove_invalid(wordlist: set[str], filters: list[callable]) -> set[str]:
        return {
            word for word in wordlist
            if all(
                (check(word) for check in filters)
            )  # check all filter validate the word
        }

    @staticmethod
    def remove_duplicates(wordlist: list[str]) -> set[str]:
        return {*map(str.lower, wordlist)}

    def filter_wordlist(self, wordlist_filters=(), use_default_filters: bool = True):
        self.wordlist = self.remove_invalid(
            self.wordlist,
            [
                *(self.default_filters if use_default_filters else []),
                *wordlist_filters,
            ]

        )


class Solver:
    FILENAME = "./wordlist.txt"

    UNKNOWN = "?"
    KNOWN = "."
    INVALID = "x"

    def __init__(self, filename: str = FILENAME):
        self.wordlist = Wordlist(filename)
        self.wordlist.filter_wordlist(use_default_filters=True)

        self.filters = []
        self.known_letters = set()
        self.frequency_table = {}

    @staticmethod
    def calculate_best_word(wordlist: Wordlist, heuristic: callable):
        return max(wordlist, key=heuristic)

    @staticmethod
    def valid_position(letter: str, position: int) -> callable:
        return lambda w: w[position] == letter

    @staticmethod
    def invalid_position(letter: str, position) -> callable:
        return lambda w: letter in w and not w[position] == letter

    @staticmethod
    def invalid_letter(letter: str) -> callable:
        return lambda w: letter not in w

    def frequency_analysis(self):
        combined_wordlist = "".join(self.wordlist)
        self.frequency_table = {
            letter: combined_wordlist.count(letter) for letter in lowercase
        }

    def handle_result(self, word: str, result: str) -> list[callable]:
        if len(result) > self.wordlist.WORD_SIZE:
            raise ValueError(f"{result} exceeds word size: {self.wordlist.WORD_SIZE}")
        for i, (letter, response) in enumerate(zip(word, result)):
            match response:
                case self.INVALID:
                    if letter in self.known_letters:
                        yield self.invalid_position(letter, i)
                    else:
                        yield self.invalid_letter(letter)
                case self.UNKNOWN:
                    yield self.invalid_position(letter, i)
                case self.KNOWN:
                    self.known_letters.add(letter)
                    yield self.valid_position(letter, i)
                case _:
                    raise ValueError(f"Unknown symbol {response}")

    def solve(self, heuristic: callable = None):

        if heuristic is None:
            heuristic = lambda w: sum(
                (self.frequency_table[letter] for letter in {*w})
            )

        print(f"{self.KNOWN} if the letter is in the correct position")
        print(f"{self.UNKNOWN} if the letter is in the incorrect position")
        print(f"{self.INVALID} if the letter is not in the word")

        while True:
            self.wordlist.filter_wordlist(self.filters, use_default_filters=False)
            self.frequency_analysis()
            best_word = self.calculate_best_word(self.wordlist, heuristic)
            print(best_word)
            result = input("> ")
            if result == "." * self.wordlist.WORD_SIZE:
                break
            self.filters.extend(self.handle_result(best_word, result))


if __name__ == '__main__':
    Solver().solve()
