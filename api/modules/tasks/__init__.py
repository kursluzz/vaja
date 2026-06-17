from api.modules import VajaModule, register
from api.modules.tasks.router import router

register(
    VajaModule(
        name="tasks",
        display_name="Task Management",
        router=router,
    )
)
