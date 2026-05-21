from __future__ import annotations

from datetime import datetime, timedelta, timezone

import boto3


def get_volume_bytes_used(session: boto3.Session, cluster_ids: list[str]) -> dict[str, float]:
    """Returns a mapping of cluster_id -> volume bytes used (latest value)."""
    if not cluster_ids:
        return {}

    client = session.client("cloudwatch")
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=1)

    queries = []
    for i, cluster_id in enumerate(cluster_ids):
        queries.append({
            "Id": f"m{i}",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/DocDB",
                    "MetricName": "VolumeBytesUsed",
                    "Dimensions": [
                        {"Name": "DBClusterIdentifier", "Value": cluster_id},
                    ],
                },
                "Period": 300,
                "Stat": "Average",
            },
        })

    result = {}
    # GetMetricData accepts max 500 queries per call
    for batch_start in range(0, len(queries), 500):
        batch = queries[batch_start : batch_start + 500]
        response = client.get_metric_data(
            MetricDataQueries=batch,
            StartTime=start,
            EndTime=now,
        )
        for metric in response["MetricDataResults"]:
            idx = int(metric["Id"][1:])
            cluster_id = cluster_ids[batch_start + idx]
            if metric["Values"]:
                result[cluster_id] = metric["Values"][0]

    return result
