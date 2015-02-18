from charlatan.utils import is_sqlalchemy_model


class Builder(object):

    def __call__(self, fixtures, klass, params, **kwargs):
        """Build a fixture.

        :param FixturesManager fixtures:
        :param klass: the fixture's class (``model`` in the definition file)
        :param params: the fixture's params (``fields`` in the definition
            file)
        :param dict kwargs:

        ``kwargs`` allows passing arguments to the builder to change its
        behavior.
        """
        raise NotImplementedError


class InstantiateAndSave(Builder):

    def __call__(self, fixtures, klass, params, **kwargs):
        """Save a fixture instance.

        If it's a SQLAlchemy model, it will be added to the session and
        the session will be committed.

        Otherwise, a :meth:`save` method will be run if the instance has
        one. If it does not have one, nothing will happen.

        Before and after the process, the :func:`before_save` and
        :func:`after_save` hook are run.

        """
        session = kwargs.get('session')
        save = kwargs.get('save')

        instance = self.instantiate(klass, params)
        if save:
            self.save(instance, fixtures, session)
        return instance

    def instantiate(self, klass, params):
        """Return instantiated instance."""
        try:
            return klass(**params)
        except TypeError as exc:
            raise TypeError("Error while trying to build %r "
                            "with %r: %s" % (klass, params, exc))

    def save(self, instance, fixtures, session):
        """Save instance."""
        fixtures.get_hook("before_save")(instance)

        if session and is_sqlalchemy_model(instance):
            session.add(instance)
            session.commit()

        else:
            getattr(instance, "save", lambda: None)()

        fixtures.get_hook("after_save")(instance)


class DeleteAndCommit(Builder):

    def __call__(self, fixtures, instance, **kwargs):
        session = kwargs.get('session')
        commit = kwargs.get('commit')

        fixtures.get_hook("before_uninstall")()
        try:
            if commit:
                self.delete(instance, session)
            else:
                try:
                    getattr(instance, "delete_instance")()
                except AttributeError:
                    getattr(instance, "delete", lambda: None)()

        except Exception as exc:
            fixtures.get_hook("after_uninstall")(exc)
            raise

        else:
            fixtures.get_hook("after_uninstall")(None)

    def delete(self, instance, session):
        """Delete instance."""
        if session and is_sqlalchemy_model(instance):
            session.delete(instance)
            session.commit()
