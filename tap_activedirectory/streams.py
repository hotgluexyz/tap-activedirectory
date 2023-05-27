"""Stream type classes for tap-activedirectory."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th 

from tap_activedirectory.client import ActivedirectoryStream
import csv
import requests
import json
from io import StringIO
from singer_sdk.helpers.jsonpath import extract_jsonpath


class UsersStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "users"
    path = "/v1.0/users"
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

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "user_id": record["id"],
        }

class SecureScoreStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "secure_score"
    path = "/v1.0/security/secureScores"
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
        th.Property("averageComparativeScores", th.ArrayType(th.CustomType({"type": ["object", "string"]}))),
        th.Property("controlScores", th.ArrayType(th.CustomType({"type": ["object", "string"]}))),
        th.Property("vendorInformation", th.ObjectType(
            th.Property("provider", th.StringType),
            th.Property("providerVersion", th.StringType),
            th.Property("subProvider", th.StringType),
            th.Property("vendor", th.StringType),
        )),
    ).to_dict()

class AccountStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "account"
    path = "/v1.0/me"
    primary_keys = ["id"]
    replication_key = None
    records_jsonpath = "$.[*]"
    schema = th.PropertiesList(
        th.Property("@odata.context", th.StringType),
        th.Property("businessPhones", th.ArrayType(th.StringType)),
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

class ActivityStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "activity"
    path = "/v1.0/reports/getM365AppUserDetail(period='D180')"
    primary_keys = ["userPrincipalName"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("Report Refresh Date", th.DateTimeType),
        th.Property("User Principal Name", th.StringType),
        th.Property("Last Activation Date", th.DateTimeType),
        th.Property("Last Activity Date", th.DateTimeType),
        th.Property("Report Period", th.IntegerType),
        th.Property("Windows", th.BooleanType),
        th.Property("Mac", th.BooleanType),
        th.Property("Mobile", th.BooleanType),
        th.Property("Web", th.BooleanType),
        th.Property("Outlook", th.BooleanType),
        th.Property("Word", th.BooleanType),
        th.Property("Excel", th.BooleanType),
        th.Property("PowerPoint", th.BooleanType),
        th.Property("OneNote", th.BooleanType),
        th.Property("Teams", th.BooleanType),
        th.Property("Outlook (Windows)", th.BooleanType),
        th.Property("Word (Windows)", th.BooleanType),
        th.Property("Excel (Windows)", th.BooleanType),
        th.Property("PowerPoint (Windows)", th.BooleanType),
        th.Property("OneNote (Windows)", th.BooleanType),
        th.Property("Teams (Windows)", th.BooleanType),
        th.Property("Outlook (Mac)", th.BooleanType),
        th.Property("Word (Mac)", th.BooleanType),
        th.Property("Excel (Mac)", th.BooleanType),
        th.Property("PowerPoint (Mac)", th.BooleanType),
        th.Property("OneNote (Mac)", th.BooleanType),
        th.Property("Teams (Mac)", th.BooleanType),
        th.Property("Outlook (Mobile)", th.BooleanType),
        th.Property("Word (Mobile)", th.BooleanType),
        th.Property("Excel (Mobile)", th.BooleanType),
        th.Property("PowerPoint (Mobile)", th.BooleanType),
        th.Property("OneNote (Mobile)", th.BooleanType),
        th.Property("Teams (Mobile)", th.BooleanType),
        th.Property("Outlook (Web)", th.BooleanType),
        th.Property("Word (Web)", th.BooleanType),
        th.Property("Excel (Web)", th.BooleanType),
        th.Property("PowerPoint (Web)", th.BooleanType),
        th.Property("OneNote (Web)", th.BooleanType),
        th.Property("Teams (Web)", th.BooleanType),
        
    ).to_dict()

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        if response.status_code not in [404]:
            reader = csv.DictReader(StringIO(response.text))
            result_list = list(reader)
            yield from extract_jsonpath(self.records_jsonpath, input=result_list)
    
    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        return None

class MFAStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "MFA"
    path = "/beta/reports/authenticationMethods/userRegistrationDetails"
    primary_keys = ["id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("userPrincipalName", th.StringType),
        th.Property("userDisplayName", th.StringType),
        th.Property("isAdmin", th.BooleanType),
        th.Property("isSsprRegistered", th.BooleanType),
        th.Property("isSsprEnabled", th.BooleanType),
        th.Property("isSsprCapable", th.BooleanType),
        th.Property("isMfaRegistered", th.BooleanType),
        th.Property("isMfaCapable", th.BooleanType),
        th.Property("isPasswordlessCapable", th.BooleanType),
        th.Property("methodsRegistered", th.ArrayType(th.StringType)),
        th.Property("defaultMethod", th.StringType),
        th.Property("userType", th.StringType),
    ).to_dict()

class LicensesStream(ActivedirectoryStream):
    """Define custom stream."""
    name = "licenses"
    path = "/v1.0/users/{user_id}/licenseDetails"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = UsersStream
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("user_id", th.StringType),
        th.Property("skuId", th.StringType),
        th.Property("skuPartNumber", th.StringType),
        th.Property("servicePlans", th.ArrayType(
            th.ObjectType(
                th.Property("servicePlanId", th.StringType),
                th.Property("servicePlanName", th.StringType),
                th.Property("provisioningStatus", th.StringType),
                th.Property("appliesTo", th.StringType),
            )
        )),
    ).to_dict()
