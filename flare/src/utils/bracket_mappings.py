import logging
from pathlib import Path

logger = logging.getLogger("luigi-interface")


class BracketMappings:
    """
    This class is a way to centralise the bracket mappings used inside production_types.yaml.

    The idea being that if in the future the brackets change OR new ones are added then this central
    class is where the change is made and everything else will continue.

    Bracket Mapping Types
    ----------------------
    `output` = ()
        Denotes an output file
    `input` = --
        Denotes an input file from a previous stage in the MC production workflow
    `datatype_parameter` = ++
        Inside the MCProductionBaseClass there exits the datatype parameter. If a given
        arg requires this specific datatype parameter in its name then it is parsed and added
        during runtime
    `free_name` = <>
        Denotes where the analyst can take liberties with their naming convention

    Methods
    ---------
    `determine_bracket_mapping`:
        This method takes an argument from the production_types.yaml and checks if there is
        an associated mapping inside this class
    """

    output = "()"
    input = "--"
    datatype_parameter = "++"
    free_name = "<>"

    @staticmethod
    def determine_bracket_mapping(arg: str) -> str | None:
        """
        Given a arg (type string) this method will check all attributes of the class
        in an attempt to match the arg with one of the attributes.

        Returns:
            value : str
                The matched string
            None:
                if no attribute is matched
        """
        for name, value in BracketMappings.__dict__.items():
            try:
                if "__" not in name and value in arg:  # Ignore special attributes
                    return value
            except TypeError:
                continue
        return None


def _strip(arg, mapping: BracketMappings):
    """
    This method does nothing more than strip the free name
    brackets from the argument
    """
    return arg.replace(mapping[0], "").replace(mapping[1], "")


def check_if_path_matches_mapping(arg: str, path: str | Path, mapping: str) -> bool:
    """
    This function returns True if an argument matches a path

    Returns False when there is an argument that does not have a matching path
    """
    args = _strip(arg, mapping).split("_")
    return all([(arg in str(path)) for arg in args])


def get_suffix_from_arg(arg) -> str:
    """
    For a given arg, get the suffix
    """
    return str(Path(arg).suffix)


class BracketMappingCMDBuilderMixin:

    unparsed_args = []

    def get_file_paths(self):
        raise NotImplementedError

    def cmd_files_dir(self):
        file = next(iter(self.get_file_paths()))
        if not isinstance(file, Path):
            file = Path(file)
        return file.parent

    def bm_output(self) -> Path:
        raise NotImplementedError

    def bm_input(self) -> Path:
        raise NotImplementedError

    def bm_datatype_parameter(self, arg: str) -> Path:
        raise NotImplementedError

    def bm_free_name(self, arg: str) -> Path:
        raise NotImplementedError

    def collect_cmd_inputs(self) -> list:
        """
        Here should be the code required to get the ordered
        list of inputs for the given MC production type

        We rely on the BracketMappings class to handle transformations
        along with the helper functions inside production_types.py

        """
        logger.info("Gathering cmd arguments for cmd")
        cmd_inputs = []
        for arg in self.unparsed_args:
            # Match the type of argument
            match BracketMappings.determine_bracket_mapping(arg):
                case BracketMappings.output:
                    path = self.bm_output()
                    cmd_inputs.append(str(path))

                case BracketMappings.input:
                    path = self.bm_input()
                    cmd_inputs.append(str(path))

                case BracketMappings.datatype_parameter:
                    path = self.bm_datatype_parameter(arg=arg)
                    cmd_inputs.append(str(path))

                case BracketMappings.free_name:
                    # Find the associated file using the check_if_path_maetches_mapping function
                    path = self.bm_free_name(arg=arg)
                    cmd_inputs.append(str(path))

                case _:
                    raise FileNotFoundError(
                        f"There is no file in {self.cmd_files_dir()} that"
                        f" matches {arg}. Please ensure all files are present"
                    )
        return cmd_inputs
