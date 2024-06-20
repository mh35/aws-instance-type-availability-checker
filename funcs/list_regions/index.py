"""リージョン一覧を生成します."""

from typing import TYPE_CHECKING, Any, TypedDict

import boto3

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext

class EventDict(TypedDict):
    """イベントの型です."""

    region: str

def handler(event: dict[str, Any], context: "LambdaContext") -> list[EventDict]:
    """一覧を生成します."""
    ec2 = boto3.Session().client("ec2")
    regions_res = ec2.describe_regions()
    return [
        {"region": r["RegionName"]} for r in regions_res["Regions"]
    ]
