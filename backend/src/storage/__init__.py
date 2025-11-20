"""Storage layer for templates and documents."""

from .template_store import (
    TemplateStore,
    TemplateStoreError,
    TemplateNotFoundError,
    get_template_store,
)
from .document_store import (
    DocumentStore,
    DocumentStoreError,
    DocumentNotFoundError,
    get_document_store,
)

__all__ = [
    "TemplateStore",
    "TemplateStoreError",
    "TemplateNotFoundError",
    "get_template_store",
    "DocumentStore",
    "DocumentStoreError",
    "DocumentNotFoundError",
    "get_document_store",
]
