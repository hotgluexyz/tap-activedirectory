"""Stream type classes for tap-activedirectory."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th 

from tap_activedirectory.client import ActivedirectoryStream


class UsersStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "users"
    path = "/users"
    primary_keys = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("businessPhones", th.ArrayType(th.CustomType({"type": ["object", "string"]}))),
        th.Property("displayName", th.StringType),
        th.Property("givenName", th.StringType),
        th.Property("jobTitle", th.StringType),
        th.Property("mail", th.StringType),
        th.Property("mobilePhone", th.StringType),
        th.Property("officeLocation", th.StringType),
        th.Property("preferredLanguage", th.StringType),
        th.Property("surname", th.StringType),
        th.Property("userPrincipalName", th.StringType),
        th.Property("id", th.StringType),
    ).to_dict()


class AccountsStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "accounts"
    path = "/security/secureScores"
    primary_keys = ["id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("azureTenantId", th.StringType),
        th.Property("activeUserCount", th.IntegerType),
        th.Property("createdDateTime", th.DateTimeType),
        th.Property("currentScore", th.NumberType),
        th.Property("enabledServices", th.ArrayType(th.StringType)),
        th.Property("licensedUserCount", th.IntegerType),
        th.Property("activeUserCount", th.IntegerType),
        th.Property("maxScore", th.NumberType),
        th.Property("averageComparativeScores", th.ObjectType(
            th.Property("basis", th.StringType),
            th.Property("averageScore", th.NumberType),
        )),
        th.Property("controlScores", th.ObjectType(
            th.Property("controlCategory", th.StringType),
            th.Property("controlName", th.StringType),
            th.Property("description", th.StringType),
            th.Property("score", th.NumberType),
        )),
        th.Property("vendorInformation", th.ObjectType(
            th.Property("provider", th.StringType),
            th.Property("providerVersion", th.StringType),
            th.Property("subProvider", th.StringType),
            th.Property("vendor", th.NumberType),
        )),
    ).to_dict()
