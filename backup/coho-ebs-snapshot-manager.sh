#!/bin/sh
#
# coho-ebs-snapshot-manager.sh - daily snapshot management script
#
# Create new snapshots of the coho filesystems.  Delete old snapshots.
# This script is executed daily by cron.
#

set -eux

#
# Create today's snapshots
#
YYYYMMDD=`/bin/date +%Y%m%d`
DAY=`/bin/date +%d`

# Stop services to prevent filesystem changes
/etc/init.d/apache2 stop
/etc/init.d/mysql stop

# Flush buffers to disk
/bin/sync

# Prevent writes to filesystem by anything we failed to stop
for MOUNTPOINT in / /var/www /var/lib/mysql; do
  /sbin/fsfreeze -f $MOUNTPOINT
done

if [ "$DAY" == "01" ] ; then
  TAGS=--tag-specifications "ResourceType=snapshot,Tags=[{Key=Type,Value=Monthly}]"
else
  TAGS=--tag-specifications "ResourceType=snapshot,Tags=[{Key=Type,Value=Daily}]"
fi  

# Create the snapshots
/usr/bin/aws ec2 create-snapshot \
  --volume-id vol-0ebc31751ee23c086 \
  --description "/ $YYYYMMDD" \
  --region us-west-2 \
  --tag-specifications $TAGS
	
/usr/bin/aws ec2 create-snapshot \
  --volume-id vol-07a475b8d450db3ef \
  --description "/var/www $YYYYMMDD" \
  --region us-west-2 \
  --tag-specifications $TAGS

/usr/bin/aws ec2 create-snapshot \
  --volume-id vol-0559ccba5975f9745 \
  --description "/var/lib/mysql $YYYYMMDD" \
  --region us-west-2 \
  --tag-specifications $TAGS

# The snapshots are started.  They won't be complete for a few minutes but we can start the
# system back up now; we just needed quiet filesystems in order to start the snapshots.

# Allow writes to filesystems
for MOUNTPOINT in / /var/www /var/lib/mysql do;
  /sbin/fsfreeze -u $MOUNTPOINT
done

# Restart services
/etc/init.d/mysql start
/etc/init.d/apache2 start


#
# Delete old snapshots
#
# Keep the last 7 days of daily snapshots
# Keep a snapshot from the first of every month for 1 year
# Delete everything else.

#
# Find snapshots that were not taken on the first of the month that are older than 7 days.  Delete them.
#
SEVEN_DAYS_AGO=`date -d '7 days ago' +%Y-%m-%d`
SNAPSHOTS=($(/usr/bin/aws ec2 describe-snapshots --region us-west-2 --owner-ids 660983422489 --filters Name=tag:Type,Values=Daily --query "Snapshots[?StartTime<\`$SEVEN_DAYS_AGO\`].SnapshotId" --output text))

echo "Would delete $SNAPSHOTS"
#for SNAPSHOT in $SNAPSHOTS; do
#  /usr/bin/aws ec2 delete-snapshot --snapshot-id $SNAPSHOT
#done

#
# Find snapshots that are older than 1 year, delete them.
#
ONE_YEAR_AGO=`date -d '1 year ago' +%Y-%m-%d`
SNAPSHOTS=($(/usr/bin/aws ec2 describe-snapshots --region us-west-2 --owner-ids 660983422489 --filters Name=tag:Type,Values=Monthly --query "Snapshots[?StartTime<\`$ONE_YEAR_AGO\`].SnapshotId" --output text))

echo "Would delete $SNAPSHOTS"
#for SNAPSHOT in $SNAPSHOTS; do
#  /usr/bin/aws ec2 delete-snapshot --snapshot-id $SNAPSHOT
#done




