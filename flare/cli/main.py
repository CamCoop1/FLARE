from flare.cli.arguments import get_args


def main():
    args = get_args()

    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
