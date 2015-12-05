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
import collections

_VersionInfo = collections.namedtuple('VersionInfo', ('major', 'minor', 'patch',))
_VERSION_INFO = _VersionInfo(major=0, minor=0, patch=1)

__author__ = 'Federico Ficarelli'
__copyright__ = 'Copyright (c) 2015 Federico Ficarelli'
__license__ = 'Apache License Version 2.0'
__version__ = '.'.join(str(v) for v in _VERSION_INFO)


__all__ = (
    'ObservableMixin',
)


class _Undefined(object):
    pass


__undefined__ = _Undefined()


class ObservableMixin(object):
    __any_event__ = '__any_event__'

    def __init__(self, *args, observable_events=__undefined__, observers=__undefined__, lock_factory=threading.RLock,
                 **kwargs):
        if observable_events is __undefined__:
            raise ValueError("parameter 'observable_events' must be specified in construction")
        super().__init__(*args, **kwargs)
        # Configuration:
        # event -> callbacks
        self._events = {ev: set() for ev in observable_events}
        self._events[self.__any_event__] = set()
        # threadsafety
        self.__lock_factory = lock_factory
        self._lock = self.__lock_factory()

    def events(self):
        yield from self._events.keys()

    def add_observer(self, callback, event=__undefined__):
        event = event if event is not __undefined__ else self.__any_event__
        if event not in self._events:
            raise KeyError('unknown specified event: {}'.format(event))
        with self._lock:
            self._events[event].add(callback)

    def remove_observer(self, callback, event=__undefined__):
        events = (event,) if event is not __undefined__ else self._events.keys()
        with self._lock:
            for event in events:
                if event in self._events and callback in self._events[event]:
                    self._events[event].remove_observer(callback)

    def _signal_observers(self, *args, event=__undefined__, **kwargs):
        if event not in self._events:
            raise KeyError('unknown specified event: {}'.format(event))
        with self._lock:
            callbacks = {
                ev: copy.copy(self._events[ev]) for ev in (event, self.__any_event__)
                }
        # Lock released, now we can calmly  invoke all callbacks:
        for ev, callbacks in callbacks.items():
            for cb in callbacks:
                cb(*args, event=event, **kwargs)
