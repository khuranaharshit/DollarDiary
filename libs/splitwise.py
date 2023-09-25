"""
Library for accessing Splitwise data for a user.
"""

import os
from splitwise import Splitwise
import logging

logger = logging.basicConfig(level=logging.INFO)

# Login to SplitWise dashboard and create an App with.
api_key = os.environ['API_KEY']