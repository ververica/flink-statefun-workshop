################################################################################
#  Licensed to the Ververica GmbH under one
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

# This file contains utility functions for the Stateful Function workshop.
# You should not need to modify anything in this file to complete the exercises.

import time
import random

from entities_pb2 import MerchantScore


def internal_query_service():
    """
    This function simulates network IO by sleeping for a random
    amount of time before returning a random trustworthiness score
    """

    time.sleep(random.randint(0, 4))

    m_score = MerchantScore()
    m_score.score = random.randint(a=0, b=100)
    return m_score
