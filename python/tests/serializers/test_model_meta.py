"""Tests for model_meta utilities."""

import pytest

from django_bolt.serializers.model_meta import (
    FieldInfo,
    RelationInfo,
    get_field_info,
    is_abstract_model,
    get_all_field_names,
    get_unique_together_constraints,
    get_unique_field_names,
)

# Import test models
from tests.test_models import (
    Article,
    Author,
    BlogPost,
    Comment,
    Tag,
    User,
    UserProfile,
    Event,
    DailyReport,
    MonthlyReport,
    YearlyReport,
    AbstractBaseModel,
    ConcreteModel,
)


class TestGetFieldInfo:
    """Tests for get_field_info function."""

    def test_returns_field_info_namedtuple(self):
        """Test that get_field_info returns a FieldInfo namedtuple."""
        info = get_field_info(Article)
        assert isinstance(info, FieldInfo)

    def test_pk_field_detection(self):
        """Test that primary key field is correctly detected."""
        info = get_field_info(Article)
        assert info.pk.name == "id"
        assert info.pk.primary_key is True

    def test_regular_fields_detection(self):
        """Test that regular fields are correctly detected."""
        info = get_field_info(Article)

        # Regular fields should be in info.fields
        assert "title" in info.fields
        assert "content" in info.fields
        assert "status" in info.fields
        assert "author" in info.fields  # CharField, not FK
        assert "is_published" in info.fields

        # Primary key should NOT be in info.fields
        assert "id" not in info.fields

    def test_fields_and_pk_includes_both(self):
        """Test that fields_and_pk includes pk and regular fields."""
        info = get_field_info(Article)

        # Should include pk
        assert "pk" in info.fields_and_pk
        assert "id" in info.fields_and_pk

        # Should include regular fields
        assert "title" in info.fields_and_pk
        assert "content" in info.fields_and_pk

    def test_forward_relations_detection(self):
        """Test that forward relations are correctly detected."""
        info = get_field_info(BlogPost)

        # ForeignKey should be in forward_relations
        assert "author" in info.forward_relations
        author_rel = info.forward_relations["author"]
        assert isinstance(author_rel, RelationInfo)
        assert author_rel.related_model == Author
        assert author_rel.to_many is False
        assert author_rel.reverse is False

        # ManyToManyField should be in forward_relations
        assert "tags" in info.forward_relations
        tags_rel = info.forward_relations["tags"]
        assert tags_rel.related_model == Tag
        assert tags_rel.to_many is True
        assert tags_rel.reverse is False

    def test_one_to_one_field_detection(self):
        """Test that OneToOneField is correctly detected."""
        info = get_field_info(UserProfile)

        assert "user" in info.forward_relations
        user_rel = info.forward_relations["user"]
        assert user_rel.related_model == User
        assert user_rel.to_many is False
        assert user_rel.reverse is False

    def test_reverse_relations_detection(self):
        """Test that reverse relations are correctly detected."""
        info = get_field_info(Author)

        # BlogPost has FK to Author, so Author should have reverse relation
        assert "posts" in info.reverse_relations
        posts_rel = info.reverse_relations["posts"]
        assert posts_rel.related_model == BlogPost
        assert posts_rel.to_many is True
        assert posts_rel.reverse is True

        # Comment also has FK to Author
        assert "comments" in info.reverse_relations

    def test_relations_combines_forward_and_reverse(self):
        """Test that relations property combines forward and reverse relations."""
        info = get_field_info(BlogPost)

        # Forward relations
        assert "author" in info.relations
        assert "tags" in info.relations

        # Reverse relation (comments)
        assert "comments" in info.relations

    def test_m2m_through_model_detection(self):
        """Test detection of explicit through models for M2M."""
        info = get_field_info(BlogPost)

        tags_rel = info.forward_relations["tags"]
        # Default auto-created through model
        assert tags_rel.has_through_model is False


class TestIsAbstractModel:
    """Tests for is_abstract_model function."""

    def test_abstract_model_returns_true(self):
        """Test that abstract models return True."""
        assert is_abstract_model(AbstractBaseModel) is True

    def test_concrete_model_returns_false(self):
        """Test that concrete models return False."""
        assert is_abstract_model(ConcreteModel) is False
        assert is_abstract_model(Article) is False
        assert is_abstract_model(Author) is False

    def test_model_inheriting_abstract_returns_false(self):
        """Test that models inheriting from abstract still return False."""
        # ConcreteModel inherits from AbstractBaseModel but is not abstract
        assert is_abstract_model(ConcreteModel) is False


class TestGetAllFieldNames:
    """Tests for get_all_field_names function."""

    def test_returns_list_of_field_names(self):
        """Test that function returns a list of field names."""
        names = get_all_field_names(Article)
        assert isinstance(names, list)

    def test_includes_pk_and_regular_fields(self):
        """Test that result includes pk and regular fields."""
        names = get_all_field_names(Article)

        assert "id" in names
        assert "title" in names
        assert "content" in names
        assert "status" in names

    def test_includes_forward_relations(self):
        """Test that result includes forward relations."""
        names = get_all_field_names(BlogPost)

        assert "author" in names
        assert "tags" in names

    def test_excludes_reverse_relations(self):
        """Test that result excludes reverse relations."""
        names = get_all_field_names(Author)

        # Reverse relations should NOT be included
        assert "posts" not in names
        assert "comments" not in names


class TestGetUniqueTogether:
    """Tests for get_unique_together_constraints function."""

    def test_detects_unique_together(self):
        """Test that unique_together constraints are detected."""
        constraints = get_unique_together_constraints(Event)

        assert len(constraints) > 0

        # Find the (venue, date, start_time) constraint
        found = False
        for fields, queryset, condition_fields, condition in constraints:
            if set(fields) == {"venue", "date", "start_time"}:
                found = True
                break

        assert found, "unique_together constraint not found"

    def test_model_without_unique_together(self):
        """Test model without unique_together returns empty list."""
        constraints = get_unique_together_constraints(Article)
        assert constraints == []


class TestGetUniqueFieldNames:
    """Tests for get_unique_field_names function."""

    def test_detects_unique_fields(self):
        """Test that unique=True fields are detected."""
        unique_fields = get_unique_field_names(User)

        assert "username" in unique_fields
        assert "email" in unique_fields

    def test_includes_primary_key(self):
        """Test that primary key is included (implicitly unique)."""
        unique_fields = get_unique_field_names(User)
        assert "id" in unique_fields

    def test_model_without_unique_fields(self):
        """Test model with only PK as unique field."""
        unique_fields = get_unique_field_names(Article)

        # Only PK should be unique
        assert "id" in unique_fields
        assert "title" not in unique_fields


class TestRelationInfo:
    """Tests for RelationInfo namedtuple."""

    def test_foreign_key_relation_info(self):
        """Test RelationInfo for ForeignKey."""
        info = get_field_info(BlogPost)
        author_rel = info.forward_relations["author"]

        assert author_rel.model_field is not None
        assert author_rel.related_model == Author
        assert author_rel.to_many is False
        # to_field is 'id' for default FK pointing to primary key
        assert author_rel.to_field in (None, 'id')
        assert author_rel.has_through_model is False
        assert author_rel.reverse is False

    def test_m2m_relation_info(self):
        """Test RelationInfo for ManyToManyField."""
        info = get_field_info(BlogPost)
        tags_rel = info.forward_relations["tags"]

        assert tags_rel.model_field is not None
        assert tags_rel.related_model == Tag
        assert tags_rel.to_many is True
        assert tags_rel.to_field is None
        assert tags_rel.reverse is False

    def test_reverse_relation_info(self):
        """Test RelationInfo for reverse relation."""
        info = get_field_info(Author)
        posts_rel = info.reverse_relations["posts"]

        # Reverse relations have None for model_field
        assert posts_rel.model_field is None
        assert posts_rel.related_model == BlogPost
        assert posts_rel.to_many is True
        assert posts_rel.reverse is True
