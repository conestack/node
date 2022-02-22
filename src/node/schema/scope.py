from contextlib import contextmanager


@contextmanager
def scope_context(context, name, parent):
    """Context manager for setting scope on context.

    Useful if ``Field`` or ``FieldSerializer`` implementations want to gather
    information from related model.

    :param context: ``ScopeContext`` instance.
    :param name: The field name in this scope.
    :param parent: The field containing model for this scope.
    """
    context.name = name
    context.parent = parent
    try:
        yield context
    finally:
        context.name = context.parent = None


class ScopeContext(object):
    """A scoped context.
    """

    name = None
    """Name of the field while scoped."""

    parent = None
    """The field containing model while scoped."""
