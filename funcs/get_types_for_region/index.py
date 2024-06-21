"""リージョンごとのインスタンスタイプ情報を取得します."""

import json
import os
import uuid
from typing import TYPE_CHECKING, TypedDict

import boto3

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext

class EventDict(TypedDict):
    """イベントの型です."""

    region: str

def handler(event: EventDict, context: "LambdaContext") -> str:
    """メイン関数です."""
    ec2 = boto3.Session(region_name=event["region"]).client("ec2")
    s3 = boto3.Session().resource("s3")
    res = ec2.describe_instance_type_offerings(
        LocationType="availability-zone-id"
    )
    ret: dict[str, list[str]] = {}
    for item in res["InstanceTypeOfferings"]:
        instance_type = item["InstanceType"]
        location = item["Location"]
        if instance_type in ret:
            ret[instance_type].append(location)
        else:
            ret[instance_type] = [location]
    while "NextToken" in res:
        res = ec2.describe_instance_type_offerings(
            LocationType="availability-zone-id",
            NextToken=res["NextToken"],
        )
        for item in res["InstanceTypeOfferings"]:
            instance_type = item["InstanceType"]
            location = item["Location"]
            if instance_type in ret:
                ret[instance_type].append(location)
            else:
                ret[instance_type] = [location]
    bucket = s3.Bucket(os.environ["BUCKET_NAME"])
    obj_name = "step_out/" + str(uuid.uuid4()) + ".json"
    bucket.put_object(Key=obj_name, Body=json.dumps(ret).encode("utf-8"))
    return obj_name
