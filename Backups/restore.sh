#!/bin/bash
# Database restore script

if [ $# -eq 0 ]; then
  echo "Usage: ./restore.sh <backup-file.sql.gz>"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found!"
  exit 2
fi

# Unzip and restore
gunzip -c "$BACKUP_FILE" | docker exec -i db psql -U user
