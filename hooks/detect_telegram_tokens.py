import argparse
import fileinput
import re

# 9 : 35 -> 45 total


TELEGRAM_BOT_TOKEN_REGEX = r"\b\d{9}:\w{35}\b"


def find_telegram_tokens(filenames):

    for line in fileinput.input(filenames, inplace=True, backup=".bak"):
        line = re.sub(TELEGRAM_BOT_TOKEN_REGEX, "", line)

        print(line, end="")

    return 0


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filenames", nargs="*", help="Filenames pre-commit believes are changed."
    )

    args = parser.parse_args()

    return find_telegram_tokens(args.filenames)


if __name__ == "__main__":

    exit(main())
