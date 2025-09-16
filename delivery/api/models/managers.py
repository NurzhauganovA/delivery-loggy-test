from tortoise.manager import Manager
from tortoise.models import Q


class ArchiveManager(Manager):

    def get_queryset(self):
        return super(ArchiveManager, self).get_queryset().filter(Q(archived=False))
