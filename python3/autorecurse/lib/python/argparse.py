from argparse import ArgumentParser, ArgumentError


class ThrowingArgumentParser(ArgumentParser):

    def error(self, message: str) -> None:
        raise ArgumentError(None, message)


