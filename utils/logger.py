#  ((...))
#  ( x x )
#   \   /
#    ^_^
#
#  Baptiste PELLARIN 2021

import logging

root_logger = logging.getLogger("passerelle_iot")
root_logger.addHandler(logging.StreamHandler())
root_logger.setLevel(logging.INFO)
