"""Tree models."""

from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from neomodel import StringProperty

from apps.schema.models.base import TimestampModel, UIDModel


class Tree(TimestampModel, UIDModel):
  """Tree model."""

  creator_uid = StringProperty(label=_('Creator UID'))
  description = StringProperty(label=_('Description'), max_length=100)
  name = StringProperty(label=_('Name'), max_length=50, required=True)

  def __str__(self):
    return self.name

  @property
  def entity_create_url(self):
    """Return entity create URL."""

    return reverse_lazy('entity-create', args=(self.uid,))

  @property
  def entity_list_url(self):
    """Return entity list URL."""

    return reverse_lazy('entity-list', args=(self.uid,))

  @property
  def entry_create_url(self):
    """Return entry create URL."""

    return reverse_lazy('entry-create', args=(self.uid,))

  @property
  def entry_list_url(self):
    """Return entry list URL."""

    return reverse_lazy('entry-list', args=(self.uid,))

  @property
  def location_create_url(self):
    """Return location create URL."""

    return reverse_lazy('location-create', args=(self.uid,))

  @property
  def location_list_url(self):
    """Return location list URL."""

    return reverse_lazy('location-list', args=(self.uid,))

  @property
  def object_read_url(self):
    """Return tree read URL."""

    return reverse('tree-manage', args=(self.uid,))

  @property
  def person_create_url(self):
    """Return person create URL."""

    return reverse_lazy('person-create', args=(self.uid,))

  @property
  def person_list_url(self):
    """Return person list URL."""

    return reverse_lazy('person-list', args=(self.uid,))

  class Meta:
    """Tree model meta."""

    app_label = 'schema'
    verbose_name = _('Tree')
    verbose_name_plural = _('Trees')