"""Activedirectory tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th 
from tap_activedirectory.streams import (
    UsersStream,
    LicensesStream,
    MFAStream,
    ActivityStream,
    AccountStream,
    SecureScoreStream
)

STREAM_TYPES = [
    UsersStream,
    LicensesStream,
    MFAStream,
    ActivityStream,
    AccountStream,
    SecureScoreStream
]


class TapActivedirectory(Tap):
    """Activedirectory tap class."""
    def __init__(
        self,
        config=None,
        catalog=None,
        state=None,
        parse_env_config=False,
        validate_config=True,
    ) -> None:
        super().__init__(config, catalog, state, parse_env_config, validate_config)
        self.config_file = config[0]

    name = "tap-activedirectory"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=True,
        ),
        th.Property(
            "tenant",
            th.StringType,
            required=True,
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
    
if __name__ == "__main__":
    TapActivedirectory.cli()
