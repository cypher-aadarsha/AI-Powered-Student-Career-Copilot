"""Structured application logging.

Deliberately excluded from every log record: passwords, JWT tokens, API keys,
and raw resume content (log a resume id, never its text) — see TDD §19/§14.
"""
import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Quiet noisy third-party loggers unless something actually goes wrong.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    for name in ("pdfminer", "pdfplumber", "PIL", "python_multipart"):
        logging.getLogger(name).setLevel(logging.WARNING)
