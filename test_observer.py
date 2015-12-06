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
    class MyObservable(Observable):
        def __init__(self, *args, **kwargs):
            events = ('ev1', 'ev2', 'ev3', None)
            super().__init__(*args, observable_events=events, **kwargs)
    return MyObservable


@pytest.fixture
def observable(observable_type):
    return observable_type()


def test_construction():
    with pytest.raises(ValueError):
        Observable()
    Observable(observable_events=('ev', ), observers={'ev': (print, print)})


def test_unknown_event(observable):
    with pytest.raises(KeyError):
        observable.add_observer(print, 'unknown')


def test_signal(observable):
    with pytest.raises(KeyError):
        observable._signal_observers(event='unknown')


def test_error(observable):
    def callback(*args, **kwargs):
        raise RuntimeError()
    observable.add_observer(callback, 'ev1')
    observable._signal_observers(event='ev1')


def test_observers(observable):
    results = set()
    def callback(*args, event=None, canary=None, **kwargs):
        assert canary == "testvalue"
        results.add(event)
    def error(*args, event=None, canary=None, **kwargs):
        raise RuntimeError()
    # Register all observers
    for ev in observable.events():
        observable.add_observer(callback, ev)
    # Register failing callback on all events:
    observable.add_observer(error)
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
