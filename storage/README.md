# Storage Directory

This directory contains user-uploaded files and saved templates.

## Structure

```
storage/
├── templates/          # Saved document templates
│   └── {template_id}/
│       ├── document.txt
│       ├── fields.json
│       └── metadata.json
└── uploads/            # Temporary upload storage
```

## Notes

- This directory is excluded from version control (see .gitignore)
- Files in `uploads/` are temporary and may be cleaned up periodically
- Template data in `templates/` persists until explicitly deleted
- In production, consider using cloud storage (S3, GCS, etc.)

## Permissions

Ensure the application has read/write permissions to this directory:

```bash
chmod -R 755 storage/
```

## Docker Volumes

When running in Docker, this directory is mounted as a volume to persist data between container restarts.
