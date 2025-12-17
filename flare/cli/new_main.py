from flare.cli.auto_importer import auto_import_registry

auto_import_registry("flare.cli.run")
auto_import_registry("flare.cli.lint")

if __name__ == "__main__":
    from flare.cli.cli_registry import get_parser

    parser = get_parser()
    args = parser.parse_args()
    print(args)
