# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sqlite3

class InlineSQLite:
    def __init__(self, dbname, autoCommit=True):
        self.autoCommit = autoCommit
        self.conn = sqlite3.connect(dbname)
        self.curs = self.conn.cursor()

    def runQuery(self, query, *args, **kwargs):
        self.curs.execute(query, *args, **kwargs)
        return [row for row in self.curs]

    def runOperation(self, command, *args, **kwargs):
        self.curs.execute(command, *args, **kwargs)
        if self.autoCommit is True:
            self.conn.commit()

    def runOperationMany(self, command, *args, **kwargs):
        self.curs.executemany(command, *args, **kwargs)
        if self.autoCommit is True:
            self.conn.commit()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()
