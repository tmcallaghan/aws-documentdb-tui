# aws-documentdb-tui

Manage your Amazon DocumentDB clusters without ever leaving the terminal.

**aws-documentdb-tui** brings the full power of the AWS DocumentDB console to your command line — fast, keyboard-driven, and distraction-free. Browse clusters, inspect instances, manage snapshots, tweak parameter groups, and monitor performance metrics, all from a beautiful terminal interface that works everywhere Python runs.

## Why?

- **Stay in flow** — no browser tab switching, no clicking through console pages
- **Lightning fast** — navigate your entire fleet in seconds with keyboard shortcuts
- **Works anywhere** — SSH sessions, remote jump boxes, local dev machines, Windows, macOS, Linux
- **Real-time insight** — see cluster status, storage usage, and CloudWatch metrics at a glance

## Quick Start

```bash
pip install -e .
docdb-tui --profile my-aws-profile --region us-east-1
```

## Features

- Cluster overview with status, engine version, instance count, storage usage, and parameter groups
- Keyboard-driven navigation with refresh-on-demand
- Built on [Textual](https://github.com/Textualize/textual) for a rich, modern terminal experience
- Powered by boto3 with support for AWS profiles and region selection

## Requirements

- Python 3.9+
- AWS credentials with the following minimum IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBClusters",
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData"
      ],
      "Resource": "*"
    }
  ]
}
```

## License

Apache 2.0
