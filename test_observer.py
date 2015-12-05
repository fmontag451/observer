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

from observer import *


class MyObservable(ObservableMixin):

    def __init__(self, *args, **kwargs):
        events = ('ev1', 'ev2', 'ev3')
        super().__init__(*args, observable_events=events, **kwargs)


def test_observer():
    results = set()

    def callback(*args, event=None, canary=None, **kwargs):
        assert canary == "TESTVALUE"
        results.add(event)

    obs = MyObservable()

    for ev in obs.events():
        obs.add_observer(callback, ev)

    for ev in obs.events():
        obs._signal_observers(event=ev, canary="TESTVALUE")

    assert len(results.difference(set(obs.events()))) == 0
