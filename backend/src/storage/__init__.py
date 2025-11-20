"""Storage layer for documents and templates."""
from .template_store import (
    save_template,
    load_template,
    list_templates,
    update_template,
    delete_template,
)
from .document_store import (
    save_upload,
    get_upload,
    delete_upload,
)

__all__ = [
    "save_template",
    "load_template",
    "list_templates",
    "update_template",
    "delete_template",
    "save_upload",
    "get_upload",
    "delete_upload",
]
