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
    
    def on_typing(self):
        '''
        Устанавливает обработчик, вызываемый, когда кто-то из контактов пользователя печатает сообщение.
        '''
        def decorator(func: Callable[[Dict[str, Any]], None]):
            self.on_typing_handlers.append(func)
            return func
        return decorator