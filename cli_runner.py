import argparse
import importlib
import logging
import os
from datetime import datetime, timedelta
from typing import Callable, Literal, Optional, Protocol, Union

from mypy_extensions import NamedArg
from pytimeparse.timeparse import timeparse

Main = Callable[
    [
        NamedArg(Optional[int], "dashboard_server_port"),
        NamedArg(bool, "simulation_status_bar"),
        NamedArg(bool, "auto_close"),
        NamedArg(Optional[timedelta], "run_length"),
    ],
    None,
]

from enum import Enum
from typing import Any


class RunProfile(Enum):
    NONE = "None"
    GENERATING_WEBSITE_DB_FILES = "GENERATING_WEBSITE_DB_FILES"

    @staticmethod
    def of_string(s: str) -> "RunProfile":
        s = s.upper()
        try:
            return RunProfile[s]
        except:
            raise Exception(f"{s} is not a valid run profile!")


class CliLogLevel(Enum):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    def __str__(self) -> str:
        return logging._levelToName[self.value]

    @staticmethod
    def of_string(s: str) -> "CliLogLevel":
        s = s.upper()
        try:
            return CliLogLevel[s]
        except:
            raise Exception(f"{s=} is not a valid log level!")


class DojoLogFilter(logging.Filter):
    def __init__(self) -> None:
        super().__init__("dojo")


class NotLogFilter(logging.Filter):
    def __init__(self, inner: logging.Filter):
        self.inner = inner

    def filter(self, record: logging.LogRecord) -> bool:
        return not (self.inner.filter(record))


def run_main() -> None:
    parser = argparse.ArgumentParser(description="Run a Dojo Simulation")
    default_dashboard_server_port = 8786
    dashboard_group = parser.add_mutually_exclusive_group()
    dashboard_group.add_argument(
        "--dashboard-server-port",
        type=int,
        default=default_dashboard_server_port,
        help=f"The port the dashboard should be server on. {default_dashboard_server_port=}",
    )
    dashboard_group.add_argument("--no-dashboard", action="store_true")
    parser.add_argument(
        "--run-profile",
        type=RunProfile.of_string,
        choices=list(RunProfile),
        default=RunProfile.NONE,
        help="apply a set of defaults for a pre-defined scenario",
    )
    parser.add_argument(
        "--log-level",
        type=CliLogLevel.of_string,
        choices=list(CliLogLevel),
        default=CliLogLevel.INFO,
        help="log level for dojo",
    )
    parser.add_argument(
        "--global-log-level",
        type=CliLogLevel.of_string,
        choices=list(CliLogLevel),
        default=CliLogLevel.ERROR,
        help="log level for all libraries other than dojo",
    )
    parser.add_argument("--simulation-status-bar", type=bool, default=False)
    parser.add_argument("--auto-close", type=bool, default=True)
    parser.add_argument(
        "--run-length",
        type=lambda s: timedelta(seconds=timeparse(s)),
        default=None,
        help="parsed using pytimeparse (e.g. you can use '1h')",
    )
    parser.add_argument(
        "--module", type=str, help="The module to run", default="example_backtest"
    )
    args = parser.parse_args()
    module = importlib.import_module(args.module)
    print()
    print(f"Now running: {args.module}")
    print()
    main_f: Main = module.main

    main_handler = logging.StreamHandler()
    main_handler.setLevel(args.global_log_level.value)
    main_handler.addFilter(NotLogFilter(DojoLogFilter()))
    dojo_handler = logging.StreamHandler()
    dojo_handler.setLevel(args.log_level.value)
    dojo_handler.addFilter(DojoLogFilter())
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.NOTSET,
        handlers=[dojo_handler, main_handler],
    )

    if args.no_dashboard:
        dashboard_server_port: Optional[int] = None
    else:
        dashboard_server_port = args.dashboard_server_port
    run_length = args.run_length
    auto_close = args.auto_close
    simulation_status_bar = args.simulation_status_bar

    run_profile: RunProfile = args.run_profile
    match run_profile:
        case RunProfile.NONE:
            pass
        case RunProfile.GENERATING_WEBSITE_DB_FILES:
            match args.module:
                case "examples.gmxV2_swap_orders.run":
                    run_length = timedelta(minutes=2.0)
                case _:
                    pass
        case _:
            print("Unrecognised run profile!")
    args = argparse.Namespace()  # shadow args to make bugs less likely

    call_args = {
        "dashboard_server_port": dashboard_server_port,
        "simulation_status_bar": simulation_status_bar,
        "auto_close": auto_close,
        "run_length": run_length,
    }
    call_args = {
        # let main functions use default values for run_length - we don't want to override them with the 'None' value
        k: v
        for k, v in call_args.items()
        if not (k == "run_length" and v == None)
    }
    main_f(**call_args)


if __name__ == "__main__":
    run_main()
