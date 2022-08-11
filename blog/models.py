from django.contrib.sites.models import Site
from django.db import models
from model_utils.models import TimeStampedModel
from django.conf import settings
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit.managers import TaggableManager
from meta.models import ModelMeta

from blog.middlewares import get_current_user


class TimeStampWithCreatorModel(TimeStampedModel):
    """
    Abstract base class with a creation
    and modification date and time
    """

    class Meta:
        abstract = True

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Created By",
        editable=False,
        blank=True,
        null=True,
        related_name='created_%(class)ss',
        on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Updated By",
        editable=True,
        blank=True,
        null=True,
        related_name='updated_%(class)ss',
        on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = get_current_user()
        self.updated_by = get_current_user()
        super(TimeStampWithCreatorModel, self).save(*args, **kwargs)

    save.alters_data = True


class Category(TimeStampWithCreatorModel, MPTTModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children')

    class Meta:
        unique_together = ("name", "parent")

    class MPTTMeta:
        order_insertion_by = ['name']


class Blog(ModelMeta, TimeStampWithCreatorModel):
    sites = models.ManyToManyField(Site)
    author = models.CharField(null=True, max_length=255, blank=True)
    is_scrapped = models.BooleanField(default=False)
    scrapped_source = models.URLField(null=True)
    headline = models.CharField(max_length=255)
    summery = models.TextField(null=True)
    content = models.TextField(null=True)
    tags = TaggableManager()
    related_posts = models.ManyToManyField("self")
    category = models.ManyToManyField(Category, related_name="blogs")
