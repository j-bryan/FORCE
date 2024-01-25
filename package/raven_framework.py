#!/usr/bin/env python
# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Created on Feb 14, 2022

@author: cogljj

This is a package that properly imports Driver and runs it.
"""
import sys
import tempfile
from ravenframework.Driver import main
from gui import BasicGUI
if __name__ == '__main__':
  gui = BasicGUI('RAVEN')
  # FIXME: RAVEN gives a relative import error if we try to run main directly. Rather than
  # creating a separate script file that is permanently in the package, we create a temporary
  # file and run that. But if we can resolve that relative import error, we could just run
  # the ravenframework.Driver file directly.
  with tempfile.NamedTemporaryFile(mode='w+b', suffix='.py', buffering=0) as tmp:
    tmp.write(b'import sys; from ravenframework.Driver import main; sys.exit(main(True))')
    gui.run_script(tmp.name)
