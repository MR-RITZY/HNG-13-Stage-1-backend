import logging

info_log = logging.getLogger("app.Info")
error_log = logging.getLogger("app.error")

info_log.setLevel(logging.INFO)
error_log.setLevel(logging.ERROR)