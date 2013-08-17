# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pprint
import time

from marionette.by import By
from gaiatest.apps.base import Base
from gaiatest import GaiaTestCase

class SystemMessage(Base):

    name = "System Messages Test"

    def launch(self):
        Base.launch(self)
        time.sleep(5)


class TestSystemMessages(GaiaTestCase):

    def setUp(self):
        GaiaTestCase.setUp(self)

        self.app = SystemMessage(self.marionette)

    def set_alarm_and_kill(self, ms):
        self.app.launch()
        self.marionette.switch_to_frame(self.apps.displayed_app.frame)
        self.marionette.execute_script("""
          window.navigator.mozAlarms.add(new Date(Date.now() + %d), "honorTimezone", {})
        """%ms)
        self.apps.kill_all()

    def test_simple(self):
        self.app.launch()
        self.marionette.switch_to_frame(self.apps.displayed_app.frame)
        self.assertEqual('success', self.marionette.execute_async_script("""
          window.navigator.mozAlarms.add(new Date(), "honorTimezone", {})
          window.navigator.mozSetMessageHandler('alarm', function() {
            window.navigator.mozSetMessageHandler('alarm', null);
            marionetteScriptFinished('success');
          });
        """))

    def test_app_started(self):
        self.set_alarm_and_kill(1000)
        running = self.apps.runningApps()
        c = len(running)
        pprint.pprint(running)

        time.sleep(1.5)

        self.marionette.switch_to_frame()
        running = self.apps.runningApps()
        pprint.pprint(running)
        self.assertEqual(len(running), c + 1)

    def test_pending_message(self):
        self.set_alarm_and_kill(500)
        time.sleep(1)

        # app should already be launched in the background, but this seems like the only way to switch to the newest frame.
        self.apps.launch('System Messages Test')
        self.assertTrue(self.marionette.execute_script("""
          return window.navigator.mozHasPendingMessage('alarm');
        """))
