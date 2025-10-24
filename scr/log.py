import logging, sys

info_log = logging.getLogger("app.Info")
error_log = logging.getLogger("app.error")

info_log.setLevel(logging.INFO)
error_log.setLevel(logging.ERROR)


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s" )

console_handler.setFormatter(formatter)


info_log.addHandler(console_handler)
error_log.addHandler(console_handler)