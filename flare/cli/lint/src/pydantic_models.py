from typing import ClassVar, Dict, List, Optional, Set

from pydantic import Field, root_validator

from flare.src.pydantic_models.utils import ForbidExtraBaseModel


class FlaggableVariable(ForbidExtraBaseModel):
    """
    A Flaggable Variable is one that the FLARE linter is actively in search for.
    Currently these are

        - inputDir
        - outputDir
    We want to keep record of the value of these flaggable variables and their line
    numbers. This model will validate the associated data.
    """

    value: str
    lineno: int

    @classmethod
    def register(cls, value: str, lineno: int):
        return cls(value=value, lineno=lineno)


class IdentifiedPathEntry(ForbidExtraBaseModel):
    """
    An identified path is one that returns `True` against the general `looks_like_path`
    function found in {ADD PATH}

    If we find a path-like object, we must record the following information
        - path; the string associated to identified path
        - is_fstring; if the identified string is composed as an f-string
        - references; if it is an f-string, we want to know what variables it references
        - noqa; stores true if the user has specified noqa to indicate we want to skip over this
        - lineno; the line number of the variable
        - end_lineno; if the path is constructed over multiple lines, we capture the final line number
            usually its the same as lineno
    """

    path: str
    is_fstring: bool
    references: List[str]
    noqa: bool
    lineno: int
    end_lineno: int

    @classmethod
    def register(
        cls,
        path: str,
        is_fstring: bool,
        references: List[str],
        noqa: bool,
        lineno: int,
        end_lineno: int,
    ):
        return cls(
            path=path,
            is_fstring=is_fstring,
            references=references,
            noqa=noqa,
            lineno=lineno,
            end_lineno=end_lineno,
        )


class AnalyzerModel(ForbidExtraBaseModel):
    """
    Analyzer model for the linting of FCCanalysis scripts.

    We piggy-back on the Pydantic Model itself to create a class level registry that
    can be used to build a set of inputs using the builder method. i.e

    ```python
    analyzer_model = AnalyzerModel.register_flaggable_variable(
        "inputDir", value="hello/world", lineno=24
    ).register_identified_path_variables(
        name="inputdir",
        path="hello/world",
        is_fstring=False,
        references=[],
        noqa=True,
        lineno=30,
        end_lineno=30,
    )
    ```
    In this way we can build up a database before we actually validate. When we are ready, we can call

    ```python
    analyzer_model.validate_registered_data()
    ```

    This class method will take the database of registered information, an create an instance of the AnalyzerModel
    which then employs Pydantic validation on the backend the ensure everything is correct. We then pass back the
    validated Pydantic Model.

    """

    flaggable_variables: Dict[str, FlaggableVariable] = Field(default_factory=dict)
    identified_path_variables: Dict[str, IdentifiedPathEntry] = Field(
        default_factory=dict
    )

    # allowed keys (not model fields)
    VALID_VARIABLE_KEYS: ClassVar[Set[str]] = {
        "inputDir",
        "outputDir",
    }

    @root_validator
    def check_allowed_dict_keys(cls, values):
        """
        Check that our `flaggable_variabels` exclusively have keys from our VALID_VARIABLE_KEYS attribute
        """
        errors = []

        variables = values.get("flaggable_variables", {})
        invalid_vars = set(variables) - cls.VALID_VARIABLE_KEYS
        if invalid_vars:
            errors.append(
                f"Invalid variable keys: {sorted(invalid_vars)} "
                f"(allowed: {sorted(cls.VALID_VARIABLE_KEYS)})"
            )

        if errors:
            raise ValueError("; ".join(errors))

        return values

    @classmethod
    def initialize_register_mode(cls):
        """
        This function serves nothing more (right now) than a way to setup the builder_dict
        and give the user a trangible entry point to set this Pydantic Model into a registration mode
        that works off a builder method.

        We register flaggable variables and identified path variables and then we use the validate_registered_data
        to validate and check
        """
        cls.builder_dict = cls._default_dict()
        return cls

    @classmethod
    def _default_dict(cls):
        """
        Get the default for this Model
        """
        return cls().dict()

    @classmethod
    def register_flaggable_variable(cls, name: str, value: str, lineno: int):
        """
        Register a flaggable variable to the database
        """
        if not hasattr(cls, "builder_dict"):
            cls.builder_dict = cls._default_dict()
        cls.builder_dict["flaggable_variables"][name] = FlaggableVariable.register(
            value=value, lineno=lineno
        )
        return cls

    @classmethod
    def register_identified_path_variables(
        cls,
        name: str,
        path: str,
        is_fstring: bool,
        references: list,
        noqa: bool,
        lineno: int,
        end_lineno: int,
    ):
        """
        Register an identified_path_variable to the database
        """
        if not hasattr(cls, "builder_dict"):
            cls.builder_dict = cls._default_dict()
        cls.builder_dict["identified_path_variables"][name] = (
            IdentifiedPathEntry.register(
                path=path,
                is_fstring=is_fstring,
                references=references,
                noqa=noqa,
                lineno=lineno,
                end_lineno=end_lineno,
            )
        )
        return cls

    @classmethod
    def registered_identified_path_variables(cls) -> dict:
        """
        Return the dictionary of registrered identified_path_variables
        """
        return cls.builder_dict()["identified_path_variables"]

    @classmethod
    def validate_registered_data(cls):
        """
        Validate the registered data using the Pydantic model
        """
        if not hasattr(cls, "builder_dict"):
            raise RuntimeError(
                f"Unable to validate data for {cls.__name__} as no information was registered"
            )
        return cls(**cls.builder_dict)


class Autofix(ForbidExtraBaseModel):
    """
    Model to handle the validation of the Autofix object.
    The Autofix aims to provide helpful information to users
    when errors are found during linting
    """

    description: str
    replacement: str


class Diagnostic(ForbidExtraBaseModel):
    """
    Diagnostic model to validate the data of a found Flare error
    """

    code: str
    severity: str
    message: str
    file: str
    lineno: int
    end_lineno: int
    suppressed: bool = False
    context: Optional[Dict] = {}
    autofix: Optional[Autofix] = None


if __name__ == "__main__":
    analyzer_model = AnalyzerModel.register_flaggable_variable(
        "inputDir", value="hello/world", lineno=24
    ).register_identified_path_variables(
        name="inputdir",
        path="hello/world",
        is_fstring=False,
        references=[],
        noqa=True,
        lineno=30,
        end_lineno=30,
    )
    print(analyzer_model.validate_registered_data().dict())
