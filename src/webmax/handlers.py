from typing import Callable, Dict, Any

class HandlersMixin():
    def on_start(self):
        def decorator(func: Callable[[], None]):
            self.on_start_handler = func
            return func
        return decorator

    def on_message(self):
        def decorator(func: Callable[[Dict[str, Any]], None]):
            self.on_message_handlers.append(func)
            return func
        return decorator

    def on_message_removed(self):
        def decorator(func: Callable[[Dict[str, Any]], None]):
            self.on_message_removed_handlers.append(func)
            return func
        return decorator

    def on_chat_action(self, action: str | None = None):
        def decorator(func: Callable[[Any], Any]):
            self.on_chat_action_handlers.append((action, func))
            return func
        return decorator