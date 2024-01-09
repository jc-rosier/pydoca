import logging.config

import pydoca
import tests.integration.test_app.budget.providers as providers


class Configuration(pydoca.AdaptersConfig):
    BudgetRepository = providers.InMemoryBudgetRepo
    ExchangeRateService = providers.FakeExchangeRateSvc


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        }
    },
}
logging.config.dictConfig(LOGGING_CONFIG)
