import logging as _logging
import threading as _threading

try:
    _basestring = basestring
except NameError:
    # Python 3
    _basestring = str

_logger = _logging.getLogger('pykka')


class ActorRegistry(object):
    """
    Registry which provides easy access to all running actors.

    Contains global state, but should be thread-safe.
    """

    _actor_refs = []
    _actor_refs_lock = _threading.RLock()

    @classmethod
    def broadcast(cls, message, target_class=None):
        """
        Broadcast ``message`` to all actors of the specified ``target_class``.

        If no ``target_class`` is specified, the message is broadcasted to all
        actors.

        :param message: the message to send
        :type message: picklable dict

        :param target_class: optional actor class to broadcast the message to
        :type target_class: class or class name
        """
        if isinstance(target_class, _basestring):
            targets = cls.get_by_class_name(target_class)
        elif target_class is not None:
            targets = cls.get_by_class(target_class)
        else:
            targets = cls.get_all()
        for ref in targets:
            ref.tell(message)

    @classmethod
    def get_all(cls):
        """
        Get :class:`ActorRef <pykka.actor.ActorRef>` for all running actors.

        :returns: list of :class:`pykka.actor.ActorRef`
        """
        with cls._actor_refs_lock:
            return cls._actor_refs[:]

    @classmethod
    def get_by_class(cls, actor_class):
        """
        Get :class:`ActorRef` for all running actors of the given class, or of
        any subclass of the given class.

        :param actor_class: actor class, or any superclass of the actor
        :type actor_class: class

        :returns: list of :class:`pykka.actor.ActorRef`
        """
        with cls._actor_refs_lock:
            return [
                ref for ref in cls._actor_refs
                if issubclass(ref.actor_class, actor_class)]

    @classmethod
    def get_by_class_name(cls, actor_class_name):
        """
        Get :class:`ActorRef` for all running actors of the given class
        name.

        :param actor_class_name: actor class name
        :type actor_class_name: string

        :returns: list of :class:`pykka.actor.ActorRef`
        """
        with cls._actor_refs_lock:
            return [
                ref for ref in cls._actor_refs
                if ref.actor_class.__name__ == actor_class_name]

    @classmethod
    def get_by_urn(cls, actor_urn):
        """
        Get an actor by its universally unique URN.

        :param actor_urn: actor URN
        :type actor_urn: string

        :returns: :class:`pykka.actor.ActorRef` or :class:`None` if not found
        """
        with cls._actor_refs_lock:
            refs = [
                ref for ref in cls._actor_refs
                if ref.actor_urn == actor_urn]
            if refs:
                return refs[0]

    @classmethod
    def register(cls, actor_ref):
        """
        Register an :class:`ActorRef` in the registry.

        This is done automatically when an actor is started, e.g. by calling
        :meth:`Actor.start() <pykka.actor.Actor.start>`.

        :param actor_ref: reference to the actor to register
        :type actor_ref: :class:`pykka.actor.ActorRef`
        """
        with cls._actor_refs_lock:
            cls._actor_refs.append(actor_ref)
        _logger.debug('Registered %s', actor_ref)

    @classmethod
    def stop_all(cls, block=True, timeout=None):
        """
        Stop all running actors.

        ``block`` and ``timeout`` works as for
        :meth:`ActorRef.stop() <pykka.actor.ActorRef.stop>`.

        If ``block`` is :class:`True`, the actors are guaranteed to be stopped
        in the reverse of the order they were started in. This is helpful if
        you have simple dependencies in between your actors, where it is
        sufficient to shut down actors in a LIFO manner: last started, first
        stopped.

        If you have more complex dependencies in between your actors, you
        should take care to shut them down in the required order yourself, e.g.
        by stopping dependees from a dependency's
        :meth:`on_stop() <pykka.actor.Actor.on_stop>` method.

        :returns: If not blocking, a list with a future for each stop action.
            If blocking, a list of return values from
            :meth:`pykka.actor.ActorRef.stop`.
        """
        return [ref.stop(block, timeout) for ref in reversed(cls.get_all())]

    @classmethod
    def unregister(cls, actor_ref):
        """
        Remove an :class:`ActorRef <pykka.actor.ActorRef>` from the registry.

        This is done automatically when an actor is stopped, e.g. by calling
        :meth:`Actor.stop() <pykka.actor.Actor.stop>`.

        :param actor_ref: reference to the actor to unregister
        :type actor_ref: :class:`pykka.actor.ActorRef`
        """
        removed = False
        with cls._actor_refs_lock:
            if actor_ref in cls._actor_refs:
                cls._actor_refs.remove(actor_ref)
                removed = True
        if removed:
            _logger.debug('Unregistered %s', actor_ref)
        else:
            _logger.debug(
                'Unregistered %s (not found in registry)', actor_ref)
