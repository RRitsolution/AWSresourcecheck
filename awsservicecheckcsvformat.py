import boto3
import pandas as pd


def get_regions():
    ec2 = boto3.client("ec2")
    return [r['RegionName'] for r in ec2.describe_regions()['Regions']]


def collect_resources():
    data = []
    regions = get_regions()

    for region in regions:
        ec2 = boto3.client("ec2", region_name=region)

        # --- EC2 Instances ---
        try:
            instances = ec2.describe_instances()
            for r in instances.get('Reservations', []):
                for i in r.get('Instances', []):
                    data.append({
                        "Service": "EC2",
                        "ResourceId": i['InstanceId'],
                        "Region": region,
                        "Details": (
                            f"Type={i['InstanceType']}, "
                            f"State={i['State']['Name']}, "
                            f"AZ={i['Placement']['AvailabilityZone']}"
                        )
                    })
        except Exception:
            pass

        # --- EBS Volumes ---
        try:
            volumes = ec2.describe_volumes()
            for v in volumes['Volumes']:
                data.append({
                    "Service": "EBS",
                    "ResourceId": v['VolumeId'],
                    "Region": region,
                    "Details": f"Size={v['Size']}GiB, State={v['State']}"
                })
        except Exception:
            pass

        # --- Elastic IPs ---
        try:
            eips = ec2.describe_addresses()
            for e in eips['Addresses']:
                data.append({
                    "Service": "ElasticIP",
                    "ResourceId": e.get('AllocationId', e.get('PublicIp')),
                    "Region": region,
                    "Details": (
                        f"IP={e.get('PublicIp')}, "
                        f"Instance={e.get('InstanceId')}"
                    )
                })
        except Exception:
            pass

        # --- Load Balancers ---
        try:
            elb = boto3.client("elbv2", region_name=region)
            lbs = elb.describe_load_balancers()
            for lb in lbs['LoadBalancers']:
                data.append({
                    "Service": "LoadBalancer",
                    "ResourceId": lb['LoadBalancerArn'],
                    "Region": region,
                    "Details": (
                        f"Name={lb['LoadBalancerName']}, "
                        f"Type={lb['Type']}, "
                        f"State={lb['State']['Code']}"
                    )
                })
        except Exception:
            pass

        # --- RDS Databases ---
        try:
            rds = boto3.client("rds", region_name=region)
            dbs = rds.describe_db_instances()
            for db in dbs['DBInstances']:
                data.append({
                    "Service": "RDS",
                    "ResourceId": db['DBInstanceIdentifier'],
                    "Region": region,
                    "Details": (
                        f"Engine={db['Engine']}, "
                        f"AZ={db['AvailabilityZone']}"
                    )
                })
        except Exception:
            pass

        # --- ElastiCache ---
        try:
            elasticache = boto3.client("elasticache", region_name=region)
            clusters = elasticache.describe_cache_clusters(ShowCacheNodeInfo=True)
            for c in clusters['CacheClusters']:
                data.append({
                    "Service": "ElastiCache",
                    "ResourceId": c['CacheClusterId'],
                    "Region": region,
                    "Details": (
                        f"Engine={c['Engine']}, "
                        f"Status={c['CacheClusterStatus']}"
                    )
                })
        except Exception:
            pass

        # --- DynamoDB ---
        try:
            dynamo = boto3.client("dynamodb", region_name=region)
            tables = dynamo.list_tables()
            for t in tables.get('TableNames', []):
                data.append({
                    "Service": "DynamoDB",
                    "ResourceId": t,
                    "Region": region,
                    "Details": "Table"
                })
        except Exception:
            pass

        # --- NAT Gateways ---
        try:
            ngws = ec2.describe_nat_gateways()
            for n in ngws['NatGateways']:
                data.append({
                    "Service": "NAT Gateway",
                    "ResourceId": n['NatGatewayId'],
                    "Region": region,
                    "Details": (
                        f"State={n['State']}, "
                        f"Subnet={n['SubnetId']}"
                    )
                })
        except Exception:
            pass

    # -------------------- GLOBAL SERVICES --------------------

    # S3 Buckets
    try:
        s3 = boto3.client("s3")
        buckets = s3.list_buckets()
        for b in buckets['Buckets']:
            data.append({
                "Service": "S3",
                "ResourceId": b['Name'],
                "Region": "Global",
                "Details": "S3 Bucket"
            })
    except Exception:
        pass

    # CloudFront
    try:
        cloudfront = boto3.client("cloudfront")
        dists = cloudfront.list_distributions()
        for d in dists.get("DistributionList", {}).get("Items", []):
            data.append({
                "Service": "CloudFront",
                "ResourceId": d['Id'],
                "Region": "Global",
                "Details": f"Domain={d['DomainName']}"
            })
    except Exception:
        pass

    # EKS (example region)
    try:
        eks = boto3.client("eks", region_name="us-east-1")
        clusters = eks.list_clusters()
        for c in clusters.get('clusters', []):
            data.append({
                "Service": "EKS",
                "ResourceId": c,
                "Region": "us-east-1",
                "Details": "EKS Cluster"
            })
    except Exception:
        pass

    return data


if __name__ == "__main__":
    resources = collect_resources()

    # Convert to DataFrame
    df = pd.DataFrame(resources)

    # Save to CSV & Excel
    df.to_csv("aws_resources.csv", index=False)
    df.to_excel("aws_resources.xlsx", index=False)

    print("✅ AWS payable resources exported to aws_resources.csv and aws_resources.xlsx")
