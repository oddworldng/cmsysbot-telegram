import argparse
import fileinput
import re

TELEGRAM_BOT_TOKEN_REGEX = r"\b\d{9}:\w{35}\b"


def find_telegram_tokens(filenames):
    """
    Iterate through each modified file, and remove any Telegram Bot Token found in it.
    """

    detected_issues = []

    for i, line in enumerate(fileinput.input(filenames, inplace=True)):
        if re.search(TELEGRAM_BOT_TOKEN_REGEX, line):
            line = re.sub(TELEGRAM_BOT_TOKEN_REGEX, "", line)

            detected_issues.append(
                f"Warning!! Telegram Token found in line {i+1} of"
                f"{fileinput.filename()}."
            )

        # Each line must be printed again when doing inplace modifications
        print(line, end="")

    if detected_issues:
        for issue in detected_issues:
            print(issue)

        return 1

    return 0


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("filenames", nargs="*", help="Input filenames changed.")

    args = parser.parse_args()

    return find_telegram_tokens(args.filenames)


if __name__ == "__main__":
    exit(main())
