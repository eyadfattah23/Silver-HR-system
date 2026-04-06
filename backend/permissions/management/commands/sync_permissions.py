#!/usr/bin/python3
"""
Management command to sync permissions from constants to database.

Usage:
    python manage.py sync_permissions          # Sync all permissions
    python manage.py sync_permissions --dry-run   # Preview changes without applying
    python manage.py sync_permissions --delete    # Also delete permissions not in constants
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from permissions.constants import PERMISSIONS
from permissions.models import Permission


class Command(BaseCommand):
    help = 'Sync permissions from constants.py to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete permissions that are not in constants (use with caution)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete_orphans = options['delete']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))
        
        created_count = 0
        updated_count = 0
        unchanged_count = 0
        deleted_count = 0
        
        # Get existing permission codes
        existing_codes = set(Permission.objects.values_list('code', flat=True))
        constant_codes = set(p['code'] for p in PERMISSIONS)
        
        with transaction.atomic():
            # Create or update permissions from constants
            for perm_data in PERMISSIONS:
                code = perm_data['code']
                
                try:
                    permission = Permission.objects.get(code=code)
                    # Check if update needed
                    needs_update = False
                    for field in ['name', 'description', 'resource', 'action', 'can_be_given']:
                        if getattr(permission, field) != perm_data[field]:
                            needs_update = True
                            break
                    
                    if needs_update:
                        if not dry_run:
                            for field in ['name', 'description', 'resource', 'action', 'can_be_given']:
                                setattr(permission, field, perm_data[field])
                            permission.save()
                        self.stdout.write(f'  Updated: {code}')
                        updated_count += 1
                    else:
                        unchanged_count += 1
                        
                except Permission.DoesNotExist:
                    if not dry_run:
                        Permission.objects.create(
                            code=perm_data['code'],
                            name=perm_data['name'],
                            description=perm_data['description'],
                            resource=perm_data['resource'],
                            action=perm_data['action'],
                            can_be_given=perm_data['can_be_given'],
                            is_active=True,
                        )
                    self.stdout.write(self.style.SUCCESS(f'  Created: {code}'))
                    created_count += 1
            
            # Handle orphan permissions (in DB but not in constants)
            orphan_codes = existing_codes - constant_codes
            if orphan_codes:
                self.stdout.write(self.style.WARNING(
                    f'\nPermissions in database but not in constants: {len(orphan_codes)}'
                ))
                for code in sorted(orphan_codes):
                    self.stdout.write(f'  - {code}')
                
                if delete_orphans:
                    if not dry_run:
                        deleted_count = Permission.objects.filter(code__in=orphan_codes).delete()[0]
                    else:
                        deleted_count = len(orphan_codes)
                    self.stdout.write(self.style.WARNING(
                        f'\n{"Would delete" if dry_run else "Deleted"} {deleted_count} orphan permission(s)'
                    ))
                else:
                    self.stdout.write(self.style.NOTICE(
                        '\nUse --delete flag to remove orphan permissions'
                    ))
            
            if dry_run:
                # Rollback in dry-run mode
                transaction.set_rollback(True)
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(f'Created:   {created_count}')
        self.stdout.write(f'Updated:   {updated_count}')
        self.stdout.write(f'Unchanged: {unchanged_count}')
        if delete_orphans or orphan_codes:
            self.stdout.write(f'Deleted:   {deleted_count}')
        self.stdout.write('=' * 50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS('\nPermissions synced successfully!'))
