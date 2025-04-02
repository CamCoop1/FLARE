from flare.cli.arguments import get_arguments


def main():
    args = get_arguments()

    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
