import argparse

from assistant.orchestrator import answer_question


def main():
    parser = argparse.ArgumentParser(description="Document Research Assistant")
    parser.add_argument("--team", required=True)
    parser.add_argument("--question", required=True)
    args = parser.parse_args()

    print(answer_question(args.team, args.question))


if __name__ == "__main__":
    main()
