#!/bin/bash
# Database backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
docker exec -t db pg_dumpall -U user > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "*.gz" -mtime +7 -exec rm {} \;