from typing import Callable, Dict, Any

class HandlersMixin():
    def __init__(self):
        pass

    def on_start(self):
        '''
        Устанавливает обработчик, вызываемый при старте клиента.
        '''
        def decorator(func: Callable[[], None]):
            self.on_start_handler = func
            return func
        return decorator

    def on_message(self):
        '''
        Устанавливает обработчик, вызываемый при получении нового сообщения.
        '''
        def decorator(func: Callable[[Dict[str, Any]], None]):
            self.on_message_handlers.append(func)
            return func
        return decorator

    def on_message_removed(self):
        '''
        Устанавливает обработчик, вызываемый при удалении сообщения.
        '''
        def decorator(func: Callable[[Dict[str, Any]], None]):
            self.on_message_removed_handlers.append(func)
            return func
        return decorator

    def on_chat_action(self, action: str | None = None):
        '''
        Устанавливает обработчик, вызываемый при каком-либо событии в чате.
        '''
        def decorator(func: Callable[[Any], Any]):
            self.on_chat_action_handlers.append((action, func))
            return func
        return decorator