# -*- coding: utf-8 -*-
#
# Copyright 2015 Federico Ficarelli
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Types and utilities related to the `Observer Pattern <https://sourcemaking.com/design_patterns/observer>`_.
"""

import copy
import threading
import logging


__author__ = 'Federico Ficarelli'
__copyright__ = 'Copyright (c) 2015 Federico Ficarelli'
__license__ = 'Apache License Version 2.0'
__version__ = '0.0.1'


__all__ = (
    'Observable',
)


class _Undefined(object):  # pylint: disable=R0903
    """Dummy type to be used as a replacement for *unspecified* values
    in function parameters. Allows to use ``None`` as a proper value."""


__undefined__ = _Undefined()
__default_lock_factory__ = threading.RLock
__default_logger__ = logging.getLogger(__name__)


class Observable(object):
    r"""Observable type as defined in the
    `Observer Pattern <https://sourcemaking.com/design_patterns/observer>`_.

    Parameters
    ----------
    observable_events : iterable[any]
        The events that the instance will listen and trigger.
    observers : mapping[iterable], optional
        Initial observers to be registered upon instance construction.
        The value must be a mapping in the following form:
        {'event1': (callback1, callback2)}.
    logger : ``logging.Logger``, optional
        Logger object to be used for reporting.
    lock_factory : callable, optional
        Factory function used for construction of thread locks.
        Must be a callable that takes no arguments and returns a
        context manager object.
    \*args
        Extra positional arguments, ignored and forwarded to superclasses.
    \*\*kwargs
        Extra keyword arguments, ignored and forwarded to superclasses.
    """

    __any_event__ = '__any_event__'

    def __init__(self, *args, observable_events=__undefined__, observers=__undefined__, logger=__default_logger__,
                 lock_factory=__default_lock_factory__, **kwargs):
        if observable_events is __undefined__:
            raise ValueError("parameter 'observable_events' must be specified in construction")
        super().__init__(*args, **kwargs)
        self._logger = logger
        # Storage setup: event -> callbacks
        self._events = {ev: set() for ev in observable_events}
        self._events[self.__any_event__] = set()
        # Thread safety:
        self._lock = lock_factory()
        # Add initial observers
        if observers is not __undefined__:
            for ev, callbacks in observers.items():  # pylint: disable=E1101, C0103
                for cb in callbacks:  # pylint: disable=C0103
                    self.add_observer(cb, ev)

    def events(self):
        """Iterator over available events."""
        yield from self._events.keys()

    def add_observer(self, callback, event=__undefined__):
        """Register an observer for the specified event.

        Parameters
        ----------
        callback : callable
            The callback to be registered.
        event : any, optional
            The event to be registered. If omitted, the specified
            callback will be triggered by every event.
        """
        event = event if event is not __undefined__ else self.__any_event__
        if event not in self._events:
            raise KeyError('unknown specified event: {}'.format(event))
        with self._lock:
            self._events[event].add(callback)

    def remove_observer(self, callback, event=__undefined__):
        """Removes a callable from the registered observers.

        Parameters
        ----------
        callback : callable
            The callback to be removed.
        event : any, optional
            The event to be unregistered from. If omitted, the specified
            callback will be removed from every event.
        """
        events = (event,) if event is not __undefined__ else self._events.keys()
        with self._lock:
            for event in events:
                if event in self._events and callback in self._events[event]:
                    self._events[event].remove(callback)

    def _notify_observers(self, *args, event=__undefined__, **kwargs):
        r"""Notifies all observers the occurrence of an event.

        Parameters
        ----------
        event : any
            The event to be notified. Must be among the registered events for
            the instance.
        \*args
            Extra positional arguments to be forwarded to all observers.
        \*\*kwargs
            Extra keyword arguments to be forwarded to all observers.

        Notes
        -----
        Every exception raised from inside the callbacks will be ignored and
        a proper log message will be emitted.
        """
        if event is __undefined__:
            raise ValueError('event must be specified')
        if event not in self._events:
            raise KeyError('unknown specified event: {}'.format(event))
        # Add 'event' parameter to forwarded kwargs:
        kwargs['event'] = event
        # Make a tmp copy of callbacks in order to release the lock as quick as possible:
        with self._lock:
            callbacks = {
                ev: copy.copy(self._events[ev]) for ev in (event, self.__any_event__)
            }
        # Lock released, now we can invoke all callbacks:
        for event, callbacks in callbacks.items():
            for fun in callbacks:
                try:
                    fun(*args, **kwargs)
                except:  # pylint: disable=W0702
                    self._logger.exception(
                        "exception raised in callback '%s' triggered by event '%s'", fun, event)
