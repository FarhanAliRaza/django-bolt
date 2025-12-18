"""Tests for unique constraint validators."""

from datetime import date

import pytest

from django_bolt.serializers.validators import (
    UniqueValidator,
    UniqueTogetherValidator,
    UniqueForDateValidator,
    UniqueForMonthValidator,
    UniqueForYearValidator,
)

# Import test models
from tests.test_models import (
    User,
    Author,
    Event,
    DailyReport,
    MonthlyReport,
    YearlyReport,
)


class TestUniqueValidator:
    """Tests for UniqueValidator."""

    @pytest.mark.django_db
    def test_unique_validation_passes_for_new_value(self):
        """Test that validation passes for new unique value."""
        User.objects.create(username="existing", email="e@e.com", password_hash="x")

        validator = UniqueValidator(
            queryset=User.objects.all(),
            field_name="username"
        )

        # Should not raise for new value
        result = validator("new_username")
        assert result == "new_username"

    @pytest.mark.django_db
    def test_unique_validation_fails_for_existing_value(self):
        """Test that validation fails for existing value."""
        User.objects.create(username="existing", email="e@e.com", password_hash="x")

        validator = UniqueValidator(
            queryset=User.objects.all(),
            field_name="username"
        )

        with pytest.raises(ValueError) as exc:
            validator("existing")

        assert "already exists" in str(exc.value)

    @pytest.mark.django_db
    def test_unique_validation_with_none_value(self):
        """Test that None values are skipped."""
        validator = UniqueValidator(
            queryset=User.objects.all(),
            field_name="username"
        )

        result = validator(None)
        assert result is None

    @pytest.mark.django_db
    def test_unique_validation_custom_message(self):
        """Test custom error message."""
        User.objects.create(username="taken", email="t@t.com", password_hash="x")

        validator = UniqueValidator(
            queryset=User.objects.all(),
            field_name="username",
            message="Username is already taken!"
        )

        with pytest.raises(ValueError) as exc:
            validator("taken")

        assert str(exc.value) == "Username is already taken!"

    @pytest.mark.django_db
    def test_unique_validation_iexact_lookup(self):
        """Test case-insensitive uniqueness check."""
        User.objects.create(username="TestUser", email="t@t.com", password_hash="x")

        validator = UniqueValidator(
            queryset=User.objects.all(),
            field_name="username",
            lookup="iexact"
        )

        with pytest.raises(ValueError):
            validator("testuser")  # Different case but should match


class TestUniqueTogetherValidator:
    """Tests for UniqueTogetherValidator."""

    @pytest.mark.django_db
    def test_unique_together_passes_for_new_combination(self):
        """Test that validation passes for new unique combination."""
        Event.objects.create(
            name="Event1",
            venue="Venue A",
            date=date(2024, 1, 15),
            start_time="10:00"
        )

        validator = UniqueTogetherValidator(
            queryset=Event.objects.all(),
            fields=("venue", "date", "start_time")
        )

        # Different venue - should pass
        data = {
            "venue": "Venue B",
            "date": date(2024, 1, 15),
            "start_time": "10:00"
        }
        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_together_fails_for_duplicate(self):
        """Test that validation fails for duplicate combination."""
        Event.objects.create(
            name="Event1",
            venue="Venue A",
            date=date(2024, 1, 15),
            start_time="10:00"
        )

        validator = UniqueTogetherValidator(
            queryset=Event.objects.all(),
            fields=("venue", "date", "start_time")
        )

        # Same venue, date, time - should fail
        data = {
            "venue": "Venue A",
            "date": date(2024, 1, 15),
            "start_time": "10:00"
        }

        with pytest.raises(ValueError) as exc:
            validator(data)

        assert "must be unique together" in str(exc.value)

    @pytest.mark.django_db
    def test_unique_together_skips_incomplete_data(self):
        """Test that validation is skipped if required fields are missing."""
        validator = UniqueTogetherValidator(
            queryset=Event.objects.all(),
            fields=("venue", "date", "start_time")
        )

        # Missing start_time
        data = {
            "venue": "Venue A",
            "date": date(2024, 1, 15),
        }

        result = validator(data)
        assert result == data  # Should return unchanged

    @pytest.mark.django_db
    def test_unique_together_skips_null_values(self):
        """Test that validation is skipped if any field is None."""
        validator = UniqueTogetherValidator(
            queryset=Event.objects.all(),
            fields=("venue", "date", "start_time")
        )

        data = {
            "venue": "Venue A",
            "date": None,
            "start_time": "10:00"
        }

        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_together_excludes_instance_on_update(self):
        """Test that current instance is excluded on update."""
        event = Event.objects.create(
            name="Event1",
            venue="Venue A",
            date=date(2024, 1, 15),
            start_time="10:00"
        )

        validator = UniqueTogetherValidator(
            queryset=Event.objects.all(),
            fields=("venue", "date", "start_time")
        )
        validator.set_context(instance=event)

        # Same data as existing instance - should pass because it's the same record
        data = {
            "venue": "Venue A",
            "date": date(2024, 1, 15),
            "start_time": "10:00"
        }

        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_together_custom_message(self):
        """Test custom error message."""
        Event.objects.create(
            name="Event1",
            venue="Venue A",
            date=date(2024, 1, 15),
            start_time="10:00"
        )

        validator = UniqueTogetherValidator(
            queryset=Event.objects.all(),
            fields=("venue", "date", "start_time"),
            message="This time slot is already booked!"
        )

        data = {
            "venue": "Venue A",
            "date": date(2024, 1, 15),
            "start_time": "10:00"
        }

        with pytest.raises(ValueError) as exc:
            validator(data)

        assert str(exc.value) == "This time slot is already booked!"


class TestUniqueForDateValidator:
    """Tests for UniqueForDateValidator."""

    @pytest.mark.django_db
    def test_unique_for_date_passes_for_different_date(self):
        """Test that same title on different date passes."""
        DailyReport.objects.create(
            title="Status Report",
            report_date=date(2024, 1, 15),
            content="Content"
        )

        validator = UniqueForDateValidator(
            queryset=DailyReport.objects.all(),
            field="title",
            date_field="report_date"
        )

        # Same title, different date
        data = {
            "title": "Status Report",
            "report_date": date(2024, 1, 16)
        }

        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_for_date_fails_for_same_date(self):
        """Test that same title on same date fails."""
        DailyReport.objects.create(
            title="Status Report",
            report_date=date(2024, 1, 15),
            content="Content"
        )

        validator = UniqueForDateValidator(
            queryset=DailyReport.objects.all(),
            field="title",
            date_field="report_date"
        )

        data = {
            "title": "Status Report",
            "report_date": date(2024, 1, 15)
        }

        with pytest.raises(ValueError) as exc:
            validator(data)

        assert "unique for the date" in str(exc.value)

    @pytest.mark.django_db
    def test_unique_for_date_skips_missing_fields(self):
        """Test that validation is skipped if fields are missing."""
        validator = UniqueForDateValidator(
            queryset=DailyReport.objects.all(),
            field="title",
            date_field="report_date"
        )

        data = {"title": "Status Report"}  # Missing report_date
        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_for_date_excludes_instance_on_update(self):
        """Test that current instance is excluded on update."""
        report = DailyReport.objects.create(
            title="Status Report",
            report_date=date(2024, 1, 15),
            content="Content"
        )

        validator = UniqueForDateValidator(
            queryset=DailyReport.objects.all(),
            field="title",
            date_field="report_date"
        )
        validator.set_context(instance=report)

        data = {
            "title": "Status Report",
            "report_date": date(2024, 1, 15)
        }

        result = validator(data)
        assert result == data


class TestUniqueForMonthValidator:
    """Tests for UniqueForMonthValidator."""

    @pytest.mark.django_db
    def test_unique_for_month_passes_for_different_month(self):
        """Test that same category in different month passes."""
        MonthlyReport.objects.create(
            category="Sales",
            report_date=date(2024, 1, 15),
            summary="Summary"
        )

        validator = UniqueForMonthValidator(
            queryset=MonthlyReport.objects.all(),
            field="category",
            date_field="report_date"
        )

        # Same category, different month
        data = {
            "category": "Sales",
            "report_date": date(2024, 2, 15)
        }

        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_for_month_fails_for_same_month(self):
        """Test that same category in same month fails."""
        MonthlyReport.objects.create(
            category="Sales",
            report_date=date(2024, 1, 15),
            summary="Summary"
        )

        validator = UniqueForMonthValidator(
            queryset=MonthlyReport.objects.all(),
            field="category",
            date_field="report_date"
        )

        # Same category, same month (different day)
        data = {
            "category": "Sales",
            "report_date": date(2024, 1, 20)
        }

        with pytest.raises(ValueError) as exc:
            validator(data)

        assert "unique for the month" in str(exc.value)

    @pytest.mark.django_db
    def test_unique_for_month_same_month_different_year_passes(self):
        """Test that same month in different year passes."""
        MonthlyReport.objects.create(
            category="Sales",
            report_date=date(2024, 1, 15),
            summary="Summary"
        )

        validator = UniqueForMonthValidator(
            queryset=MonthlyReport.objects.all(),
            field="category",
            date_field="report_date"
        )

        # Same month number, different year
        data = {
            "category": "Sales",
            "report_date": date(2025, 1, 15)
        }

        result = validator(data)
        assert result == data


class TestUniqueForYearValidator:
    """Tests for UniqueForYearValidator."""

    @pytest.mark.django_db
    def test_unique_for_year_passes_for_different_year(self):
        """Test that same department in different year passes."""
        YearlyReport.objects.create(
            department="Engineering",
            report_date=date(2024, 6, 15),
            annual_summary="Summary"
        )

        validator = UniqueForYearValidator(
            queryset=YearlyReport.objects.all(),
            field="department",
            date_field="report_date"
        )

        # Same department, different year
        data = {
            "department": "Engineering",
            "report_date": date(2025, 6, 15)
        }

        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_for_year_fails_for_same_year(self):
        """Test that same department in same year fails."""
        YearlyReport.objects.create(
            department="Engineering",
            report_date=date(2024, 6, 15),
            annual_summary="Summary"
        )

        validator = UniqueForYearValidator(
            queryset=YearlyReport.objects.all(),
            field="department",
            date_field="report_date"
        )

        # Same department, same year (different month/day)
        data = {
            "department": "Engineering",
            "report_date": date(2024, 12, 1)
        }

        with pytest.raises(ValueError) as exc:
            validator(data)

        assert "unique for the year" in str(exc.value)

    @pytest.mark.django_db
    def test_unique_for_year_skips_none_values(self):
        """Test that None values are skipped."""
        validator = UniqueForYearValidator(
            queryset=YearlyReport.objects.all(),
            field="department",
            date_field="report_date"
        )

        data = {
            "department": None,
            "report_date": date(2024, 6, 15)
        }

        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_for_year_excludes_instance_on_update(self):
        """Test that current instance is excluded on update."""
        report = YearlyReport.objects.create(
            department="Engineering",
            report_date=date(2024, 6, 15),
            annual_summary="Summary"
        )

        validator = UniqueForYearValidator(
            queryset=YearlyReport.objects.all(),
            field="department",
            date_field="report_date"
        )
        validator.set_context(instance=report)

        data = {
            "department": "Engineering",
            "report_date": date(2024, 6, 15)
        }

        result = validator(data)
        assert result == data

    @pytest.mark.django_db
    def test_unique_for_year_custom_message(self):
        """Test custom error message."""
        YearlyReport.objects.create(
            department="Engineering",
            report_date=date(2024, 6, 15),
            annual_summary="Summary"
        )

        validator = UniqueForYearValidator(
            queryset=YearlyReport.objects.all(),
            field="department",
            date_field="report_date",
            message="Annual report already exists for this department!"
        )

        data = {
            "department": "Engineering",
            "report_date": date(2024, 12, 1)
        }

        with pytest.raises(ValueError) as exc:
            validator(data)

        assert str(exc.value) == "Annual report already exists for this department!"


class TestValidatorErrorCodes:
    """Tests for validator error codes."""

    def test_unique_validator_error_code(self):
        """Test UniqueValidator error_code property."""
        validator = UniqueValidator(queryset=None, field_name="test")
        assert validator.error_code == "unique"

    def test_unique_together_validator_error_code(self):
        """Test UniqueTogetherValidator error_code property."""
        validator = UniqueTogetherValidator(queryset=None, fields=("a", "b"))
        assert validator.error_code == "unique_together"

        # With custom code
        validator_custom = UniqueTogetherValidator(queryset=None, fields=("a", "b"), code="custom_code")
        assert validator_custom.error_code == "custom_code"

    def test_unique_for_date_validator_error_code(self):
        """Test UniqueForDateValidator error_code property."""
        validator = UniqueForDateValidator(queryset=None, field="test", date_field="date")
        assert validator.error_code == "unique_for_date"

    def test_unique_for_month_validator_error_code(self):
        """Test UniqueForMonthValidator error_code property."""
        validator = UniqueForMonthValidator(queryset=None, field="test", date_field="date")
        assert validator.error_code == "unique_for_month"

    def test_unique_for_year_validator_error_code(self):
        """Test UniqueForYearValidator error_code property."""
        validator = UniqueForYearValidator(queryset=None, field="test", date_field="date")
        assert validator.error_code == "unique_for_year"
