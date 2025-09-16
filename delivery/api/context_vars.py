from contextvars import ContextVar

locale_context: ContextVar[str] = ContextVar('locale_context', default='en')
