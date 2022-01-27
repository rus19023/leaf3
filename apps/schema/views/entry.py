"""Entry views."""

from django.utils.translation import gettext_lazy as _

from apps.schema.forms.entry import EntryForm
from apps.schema.models.entry import Entry
from apps.schema.views.base import (CreateViewBase, DeleteViewBase,
                                    ListViewBase, UpdateViewBase)


class Create(CreateViewBase):
  """Entry create view."""

  form_class = EntryForm
  model = Entry
  template_name = 'schema/entry/create.html'
  translations = {
      'add_entry': _('Add an entry'),
  }

  def get_context_data(self, **kwargs):
    """Generate context."""

    context = super().get_context_data(**kwargs)
    context.update({
        'page_header_primary_text': self.translations['add_entry'],
        'page_header_secondary_text': self.tree,
        'page_title': self.translations['add_entry'],
    })

    return context

  def get_success_url(self, **unused_kwargs):
    """Generate redirect URL."""

    return self.tree.entry_list_url


class Delete(DeleteViewBase):
  """Entry delete view."""

  model = Entry
  template_name = 'schema/entry/delete.html'

  def get_success_url(self):
    """Generate redirect URL."""

    return self.tree.entry_list_url


class List(ListViewBase):
  """Entry list view."""

  model = Entry
  ordering = 'created'
  template_name = 'schema/entry/list.html'


class Update(UpdateViewBase):
  """Entry update view."""

  form_class = EntryForm
  model = Entry
  template_name = 'schema/entry/update.html'

  translations = {
      'edit_entry': _('Edit entry'),
  }

  def get_context_data(self, **kwargs):
    """Generate context."""

    context = super().get_context_data(**kwargs)
    context.update({
        'page_header_primary_text': self.translations['edit_entry'],
        'page_header_secondary_text': self.tree,
        'page_title': self.translations['edit_entry'],
    })

    return context

  def get_success_url(self):
    """Generate redirect URL."""

    return self.tree.entry_list_url
