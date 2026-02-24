from typing import Dict

from flare.src.pydantic_models.utils.flare_task import FlareTask


def require_active(method):
    def wrapper(self, *args, **kwargs):
        assert self._active, "The Task Registry has not been activated"
        return method(self, *args, **kwargs)

    return wrapper


class RegisteredFlareTask(FlareTask):
    name: str


class TaskRegistryClass:
    _active = False
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __call__(self, *, tasks: dict[str, FlareTask]):
        registered_tasks = dict()
        for task_name, task_object in tasks.items():
            registered_task = RegisteredFlareTask(
                name=task_name, **task_object.model_dump()
            )
            registered_tasks.update({task_name: registered_task})
        self.registered_tasks: Dict[str, RegisteredFlareTask] = registered_tasks

    @require_active
    def get_task_by_name(self, task_name: str) -> RegisteredFlareTask:
        requested_task: RegisteredFlareTask = self.registered_tasks.get(task_name)
        return requested_task


TaskRegistry = TaskRegistryClass()
