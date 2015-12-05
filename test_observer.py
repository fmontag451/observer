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

import pytest

from observer import *

@pytest.fixture
def observable_type():
    class MyObservable(ObservableMixin):
        def __init__(self, *args, **kwargs):
            events = ('ev1', 'ev2', 'ev3')
            super().__init__(*args, observable_events=events, **kwargs)
    return MyObservable


@pytest.fixture
def observable(observable_type):
    return observable_type()


def test_any_event(observable):
    pass


def test_remove_observer(observable):
    pass


def test_none_event(observable):
    pass


def test_unknown_event(observable):
    with pytest.raises(KeyError):
        observable.add_observer(print, 'unknown')


def test_observers(observable):
    results = set()
    def callback(*args, event=None, canary=None, **kwargs):
        assert canary == "testvalue"
        results.add(event)
    # Register all observers
    for ev in observable.events():
        observable.add_observer(callback, ev)
    # Trigger all events
    for ev in observable.events():
        observable._signal_observers(event=ev, canary="testvalue")
    # Check that every event has been triggered
    assert len(results.difference(set(observable.events()))) == 0
    # Reset
    results.clear()
    # Remove all observers
    observable.remove_observer(callback)
    # Trigger all events
    for ev in observable.events():
        observable._signal_observers(event=ev)
    # Check that no callback has been triggered
    assert len(results) == 0
