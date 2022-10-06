from rest_framework import validators


class ObjectExistsValidator:
    """
    Checks if an object with a given set of fields exists.
    """

    def __init__(self, queryset, fields):
        self.queryset = queryset
        self.fields = fields

    def __call__(self, value):
        """Verifies that there is an object with some given fields."""
        if len(self.fields) != len(set(self.fields)):
            raise validators.ValidationError("All fields must be unique.")

        kwargs = {field: value[field] for field in self.fields if value.get(field, None) is not None}

        if len(kwargs) == 0:
            raise validators.ValidationError("No relevant fields were provided.")

        if not self.queryset.filter(**kwargs).exists():
            raise validators.ValidationError("No object was found with the given fields.")
