from typing import Dict, Optional

from pydantic import Field

from flare.src.pydantic_models.utils.flare_task import FlareTask


def require_active(method):
    """
    Wrapper that can be used on TaskRegistryClass methods that require it to be active
    to use a method.
    """

    def wrapper(self, *args, **kwargs):
        assert self._active, "The Task Registry has not been activated"
        return method(self, *args, **kwargs)

    return wrapper


class RegisteredFlareTask(FlareTask):
    """
    Essentially an extended version of a FlareTask that also has a name
    We do not initially setup our FlareTask to have a name as the YAML files
    from which these tasks are declared, we indirectly infer their name based
    on the YAML hierarchy. Here, we are explicitly declaring that name and
    this object is what will be attached to all FCC Analysis base classes
    """

    name: str
    # Here we include this as the AddFlareTask has the required_by field
    # and since we do not allow extra fields to be passed to any Pydantic
    # models in FLARE we must include it here
    required_by: Optional[list[str]] = Field(default_factory=list)


class TaskRegistryClass:
    """
    This Task Registry will serve as a singleton for the duration of the runtime of an
    FCC Analysis workflow. The idea is simple, this is the registry upon which all activate
    Tasks are kept. Inside Flare a Task is nothing more than something that adheres to the
    RegisteredFlareTask model.

    This has a __call__ method which is used once inside the dag_tooling/builder.py during the
    build_task_graph function. This function is the single place inside Flare where we identify which
    Tasks need to be ran and register them via this class.

    The TaskRegistry is to be used in conjunction with the Dag object. The Dag object is the single
    source of truth to determine the order in which Tasks should be ran. The Dag object only uses the names
    of Flare Tasks to convey the information on order. We then use this TaskRegistry to actually extract the
    Tasks and use them during runtime.
    """

    _active = False
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __call__(self, *, tasks: dict[str, FlareTask]):
        registered_tasks: Dict[str, RegisteredFlareTask] = dict()
        for task_name, task_object in tasks.items():
            registered_task = RegisteredFlareTask(
                name=task_name, **task_object.model_dump()
            )
            registered_tasks.update({task_name: registered_task})
        self.registered_tasks: Dict[str, RegisteredFlareTask] = registered_tasks
        self._active = True

    @require_active
    def get_task_by_name(self, task_name: str) -> RegisteredFlareTask:
        requested_task: RegisteredFlareTask = self.registered_tasks.get(task_name)
        return requested_task


# Define our singleton TaskRegistry
TaskRegistry = TaskRegistryClass()
