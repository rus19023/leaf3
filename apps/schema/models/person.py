"""Person models."""

from django.conf import settings
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from dateutil.relativedelta import relativedelta
from neomodel import (DateProperty, Relationship, RelationshipFrom,
                      RelationshipTo, StringProperty)

from apps.schema.models.base import TreeNodeModel
from apps.schema.models.db.relationships import TimeRangeRelationship
from apps.schema.models.location import Location


class Person(TreeNodeModel):
  """Person model."""

  FEMALE = 'F'
  MALE = 'M'

  GENDERS = {
      FEMALE: _('Female'),
      MALE: _('Male'),
  }

  GENDER_CHOICES = tuple((key, value) for key, value in GENDERS.items())

  first_name = StringProperty(label=_('First name'), max_length=25, required=True)
  patronymic_name = StringProperty(label=_('Patronymic name'), max_length=25)
  last_name = StringProperty(label=_('Last name'), required=True, max_length=50, index=True)
  maiden_name = StringProperty(label=_('Maiden name'), max_length=25)

  gender = StringProperty(label=_('Gender'), required=True, choices=GENDER_CHOICES, index=True)

  birth_place_uid = StringProperty(max_length=settings.SHORT_UUID_LENGTH)
  birth_year = StringProperty(label=_('Year of birth'), index=True)
  dob = DateProperty(label=_('Date of birth'))

  burial_place_uid = StringProperty(max_length=settings.SHORT_UUID_LENGTH)
  death_place_uid = StringProperty(max_length=settings.SHORT_UUID_LENGTH)
  death_year = StringProperty(label=_('Year of death'), index=True)
  dod = DateProperty(label=_('Date of death'))

  cod = StringProperty(label=_('Cause of death'), max_length=30, index=True)
  cod_details = StringProperty(label=_('Cause of death details'), max_length=200)

  # Persons.
  father_uid = StringProperty(max_length=settings.SHORT_UUID_LENGTH)
  mother_uid = StringProperty(max_length=settings.SHORT_UUID_LENGTH)
  spouse_uid = StringProperty(max_length=settings.SHORT_UUID_LENGTH)

  details = StringProperty(label=_('Details'), max_length=10000)

  # Locations.
  residence_uid = StringProperty(max_length=settings.SHORT_UUID_LENGTH)

  # Relationships.
  birth_place_rel = RelationshipTo('.location.Location', 'BORN_IN')
  death_place_rel = RelationshipTo('.location.Location', 'DIED_IN')
  burial_place_rel = RelationshipTo('.location.Location', 'BURIED_IN')
  employment_rel = RelationshipTo('.entity.Entity',
                                  'WORKED',
                                  model=TimeRangeRelationship)
  marriage_rel = Relationship('.person.Person',
                              'MARRIED',
                              model=TimeRangeRelationship)
  parent_rel = RelationshipFrom('.person.Person', 'PARENT')
  residence_rel = RelationshipTo('.location.Location', 'LIVED')
  spouse_rel = Relationship('.person.Person', 'SPOUSE')

  def __str__(self):
    """Person str()."""

    fields = [self.name]
    if self.summary:
      fields.append(f'({self.summary})')

    return ' '.join(fields)

  def get_name(self, format='full'):
    """Get name."""

    if self.maiden_name and format == 'full':
      fields = [f'{self.last_name}/{self.maiden_name}']
    else:
      fields = [self.last_name]

    fields.append(self.first_name)

    if self.patronymic_name and format != 'short':
      fields.append(self.patronymic_name)

    return ' '.join(fields)

  def save(self):
    """Save person model."""

    # Year of birth.
    if not self.birth_year and self.dob:
      self.birth_year = self.dob.year

    # Year of death.
    if not self.death_year and self.dod:
      self.death_year = self.dod.year

    return super().save()

  @property
  def birth_place(self):
    """Return birth place location."""

    if not self.birth_place_uid:
      return

    try:
      return Location.nodes.get(uid=self.birth_place_uid)
    except Location.DoesNotExist:
      pass

  @property
  def burial_place(self):
    """Return burial place location."""

    if not self.burial_place_uid:
      return

    try:
      return Location.nodes.get(uid=self.burial_place_uid)
    except Location.DoesNotExist:
      pass

  @property
  def children(self):
    """Return person's children."""

    query = f"""
        MATCH (Person {{ uid: "{self.uid}" }}) -[:PARENT]-> (c:Person)
        RETURN c
        ORDER BY c.birth_year DESC, c.gender DESC, c.first_name
    """

    nodes, unused_meta = self.cypher(query)
    return [self.inflate(node[0]) for node in nodes]

  @property
  def death_place(self):
    """Return death place location."""

    if not self.death_place_uid:
      return

    try:
      return Location.nodes.get(uid=self.death_place_uid)
    except Location.DoesNotExist:
      pass

  @property
  def entries(self):
    """Return person's entries."""

    query = f"""
        MATCH (entry: Entry {{ actor_uid: "{self.uid}" }})
        RETURN entry
    """

    nodes, unused_meta = self.cypher(query)
    return [self.inflate(node[0]) for node in nodes]

  @property
  def entry_create_url(self):
    """Return entry create URL."""

    return reverse_lazy('entry-create', args=(self.tree_uid, self.uid))

  @property
  def entry_list_url(self):
    """Return entry list URL."""

    return reverse_lazy('entry-list', args=(self.tree_uid, self.uid))

  @property
  def grandparents(self):
    """Return person's grandparents."""

    query = f"""
        MATCH (gp:Person) -[:PARENT]-> (p:Person) -[:PARENT]->
              (Person {{ uid: "{self.uid}" }})
        RETURN gp
        ORDER BY p.gender DESC, gp.gender DESC
    """

    nodes, unused_meta = self.cypher(query)
    return [self.inflate(node[0]) for node in nodes]

  @property
  def great_grandparents(self):
    """Return person's great-grandparents."""

    query = f"""
        MATCH (ggp: Person) -[:PARENT]-> (gp:Person) -[:PARENT]->
              (p:Person) -[:PARENT]-> (Person {{ uid: "{self.uid}" }})
        RETURN ggp
        ORDER BY p.gender DESC, gp.gender DESC, ggp.gender DESC
    """

    nodes, unused_meta = self.cypher(query)
    return [self.inflate(node[0]) for node in nodes]

  @property
  def has_children(self):
    """Return True if person has children."""

    query = f"""
        MATCH (Person {{ uid: "{self.uid}" }}) -[:PARENT]-> (c:Person)
        RETURN COUNT(c) > 0
    """

    nodes, unused_meta = self.cypher(query)
    return nodes[0][0]

  @property
  def has_parents(self):
    """Return True if person has parents."""

    query = f"""
        MATCH (Person {{ uid: "{self.uid}" }}) <-[:PARENT]- (p:Person)
        RETURN COUNT(p) > 0
    """

    nodes, unused_meta = self.cypher(query)
    return nodes[0][0]

  @property
  def is_female(self):
    """Return True if person's gender value is FEMALE."""

    return self.gender == self.FEMALE

  @property
  def is_male(self):
    """Return True if person's gender value is MALE."""

    return self.gender == self.MALE

  @property
  def long_name(self):
    """Return long name."""

    return self.get_name(format='long')

  @property
  def name(self):
    """Return full name."""

    return self.get_name()

  @property
  def object_delete_url(self):
    """Return person delete URL."""

    return reverse_lazy('person-delete', args=(self.tree_uid, self.uid))

  @property
  def object_read_url(self):
    """Return person delete URL."""

    return reverse_lazy('person', args=(self.tree_uid, self.uid))

  @property
  def object_update_url(self):
    """Return person update URL."""

    return reverse_lazy('person-update', args=(self.tree_uid, self.uid))

  @property
  def parents(self):
    """Return person's parents."""

    query = f"""
        MATCH (parent: Person) -[:PARENT]-> (Person {{ uid: "{self.uid}" }})
        RETURN parent
        ORDER BY parent.gender DESC
    """

    nodes, unused_meta = self.cypher(query)
    return [self.inflate(node[0]) for node in nodes]

  @property
  def residence(self):
    """Return residence location."""

    if not self.residence_uid:
      return

    try:
      return Location.nodes.get(uid=self.residence_uid)
    except Location.DoesNotExist:
      pass

  @property
  def siblings(self):
    """Return person's siblings."""

    query = f"""
        CALL {{
            MATCH (Person {{ uid: "{self.father_uid}" }}) -[:PARENT]-> (child:Person)
            WHERE NOT child.uid = "{self.uid}"
            RETURN child

            UNION

            MATCH (Person {{ uid: "{self.mother_uid}" }}) -[:PARENT]-> (child:Person)
            WHERE NOT child.uid = "{self.uid}"
            RETURN child
        }}

        RETURN child
        ORDER BY child.birth_year DESC, child.gender DESC, child.first_name
    """

    nodes, unused_meta = self.cypher(query)
    return [self.inflate(node[0]) for node in nodes]

  @property
  def short_name(self):
    """Return short name."""

    return self.get_name(format='short')

  @property
  def spouse(self):
    """Return spouse person."""

    if not self.spouse_uid:
      return

    try:
      return Person.nodes.get(uid=self.spouse_uid)
    except Person.DoesNotExist:
      pass

  @property
  def summary(self):
    """Return person summary information."""

    fields = []
    if self.death_year and self.death_year != '-':
      if self.birth_year:
        age = int(self.death_year) - int(self.birth_year)
        if self.is_female:
          fields.append(
              ngettext_lazy('died in {year} in the age of {f} year',
                            'died in {year} in the age of {f} years',
                            age).format(f=age, year=self.death_year))
        elif self.is_male:
          fields.append(
              ngettext_lazy('died in {year} in the age of {m} year',
                            'died in {year} in the age of {m} years',
                            age).format(m=age, year=self.death_year))
      else:
        if self.is_female:
          fields.append(_('died in {f}').format(f=self.death_year))
        elif self.is_male:
          fields.append(_('died in {m}').format(m=self.death_year))
    elif self.birth_year:
      if self.death_year == '-':
        fields.append(_('{birth_year}').format(birth_year=self.birth_year))
      else:
        age = relativedelta(now().date(), self.dob).years
        fields.append(ngettext_lazy('{n} year', '{n} years', age).format(n=age))

      if self.cod:
        fields.append(self.cod)

    children_count = len(self.children)
    if children_count:
      fields.append(
          ngettext_lazy('{c} child', '{c} children',
                        children_count).format(c=children_count))

    return ', '.join(fields)

  class Meta:
    """Person model meta."""

    app_label = 'schema'
    verbose_name = _('Person')
    verbose_name_plural = _('Persons')
