################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################
import logging
import os
import shutil
import sys
import tempfile

from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table import expressions as expr


def word_count():
    content = "line Licensed to the Apache Software Foundation ASF under one " \
              "line or more contributor license agreements See the NOTICE file " \
              "line distributed with this work for additional information " \
              "line regarding copyright ownership The ASF licenses this file " \
              "to you under the Apache License Version the " \
              "License you may not use this file except in compliance " \
              "with the License"

    t_env = TableEnvironment.create(EnvironmentSettings.in_batch_mode())

    # register Results table in table environment
    tmp_dir = tempfile.gettempdir()
    result_path = tmp_dir + '/result'
    if os.path.exists(result_path):
        try:
            if os.path.isfile(result_path):
                os.remove(result_path)
            else:
                shutil.rmtree(result_path)
        except OSError as e:
            logging.error("Error removing directory: %s - %s.", e.filename, e.strerror)

    logging.info("Results directory: %s", result_path)

    sink_ddl = """
        create table Results(
            word VARCHAR,
            `count` BIGINT
        ) with (
            'connector.type' = 'filesystem',
            'format.type' = 'csv',
            'connector.path' = '{}'
        )
        """.format(result_path)
    t_env.execute_sql(sink_ddl)

    elements = [(word, 1) for word in content.split(" ")]
    table = t_env.from_elements(elements, ["word", "count"])
    table.group_by(table.word) \
         .select(table.word, expr.lit(1).count.alias('count')) \
         .execute_insert("Results")


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    word_count()
