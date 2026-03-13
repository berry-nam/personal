#!/usr/bin/env bash
# Database backup script for kr-acc.
# Creates a timestamped pg_dump in /opt/kr-acc/backups/ and removes backups older than 7 days.
#
# Usage:
#   ./deploy/backup.sh
#
# Cron example (daily at 2am):
#   0 2 * * * cd /opt/kr-acc && ./deploy/backup.sh >> /var/log/kracc-backup.log 2>&1

set -euo pipefail

BACKUP_DIR="/opt/kr-acc/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/kracc_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup..."

docker compose exec -T db pg_dump -U kracc kracc | gzip > "$BACKUP_FILE"

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[$(date)] Backup created: $BACKUP_FILE ($SIZE)"

# Remove old backups
find "$BACKUP_DIR" -name "kracc_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
echo "[$(date)] Cleaned up backups older than ${RETENTION_DAYS} days"
