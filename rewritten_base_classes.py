from typing import Any, Optional

from aiogram import Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.fsm.middleware import FSMContextMiddleware
from aiogram.dispatcher.middlewares.error import ErrorsMiddleware
from aiogram.dispatcher.middlewares.user_context import UserContextMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.base import BaseStorage, BaseEventIsolation
from aiogram.fsm.storage.memory import MemoryStorage, DisabledEventIsolation
from aiogram.types import TelegramObject

from utils import MessageCacheChecker


class ClearCacheEventObserver(TelegramEventObserver):
    async def trigger(self, event: TelegramObject, **kwargs: Any) -> Any:
        state: FSMContext = kwargs.pop('state')
        if state and await state.get_state():
            message_text = event.message and event.message.text or event.callback_query.data
            if MessageCacheChecker(message_text).state_should_be_cleared():
                kwargs.pop('raw_state')
                await state.clear()
        kwargs['state'] = state
        triger = await super().trigger(event, **kwargs)
        return triger


class ClearCacheDispatcher(Dispatcher):
    def __init__(self,
        *,
        storage: Optional[BaseStorage] = None,
        fsm_strategy: FSMStrategy = FSMStrategy.USER_IN_CHAT,
        events_isolation: Optional[BaseEventIsolation] = None,
        disable_fsm: bool = False,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.set_custom_observer(storage, fsm_strategy, events_isolation, disable_fsm)

    def set_custom_observer(self, storage: Optional[BaseStorage],
                            fsm_strategy: FSMStrategy,
                            events_isolation: Optional[BaseEventIsolation],
                            disable_fsm: bool = False,) -> None:
        self.update = self.observers["update"] = ClearCacheEventObserver(
            router=self, event_name="update"
        )
        self.update.register(self._listen_update)

        self.update.outer_middleware(ErrorsMiddleware(self))
        self.update.outer_middleware(UserContextMiddleware())

        self.fsm = FSMContextMiddleware(
            storage=storage or MemoryStorage(),
            strategy=fsm_strategy,
            events_isolation=events_isolation or DisabledEventIsolation(),
        )
        if not disable_fsm:
            self.update.outer_middleware(self.fsm)
        self.shutdown.register(self.fsm.close)
