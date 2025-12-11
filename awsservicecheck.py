import boto3

def get_regions():
    ec2 = boto3.client("ec2")
    return [r['RegionName'] for r in ec2.describe_regions()['Regions']]

def list_resources():
    regions = get_regions()
    print("==== AWS Payable Resources Across All Regions ====\n")

    for region in regions:
        print(f"--- Region: {region} ---")

        ec2 = boto3.client("ec2", region_name=region)

        # EC2 Instances
        try:
            instances = ec2.describe_instances()
            for r in instances.get('Reservations', []):
                for i in r.get('Instances', []):
                    print(
                        f"EC2: {i['InstanceId']} | "
                        f"Type: {i['InstanceType']} | "
                        f"State: {i['State']['Name']} | "
                        f"AZ: {i['Placement']['AvailabilityZone']}"
                    )
        except Exception:
            pass

        # EBS Volumes
        try:
            volumes = ec2.describe_volumes()
            for v in volumes['Volumes']:
                print(f"EBS Volume: {v['VolumeId']} | Size: {v['Size']} GiB | State: {v['State']}")
        except Exception:
            pass

        # Elastic IPs
        try:
            eips = ec2.describe_addresses()
            for e in eips['Addresses']:
                print(f"Elastic IP: {e.get('PublicIp')} | Instance: {e.get('InstanceId')}")
        except Exception:
            pass

        # Load Balancers
        try:
            elb = boto3.client("elbv2", region_name=region)
            lbs = elb.describe_load_balancers()
            for lb in lbs['LoadBalancers']:
                print(f"LoadBalancer: {lb['LoadBalancerName']} | Type: {lb['Type']} | State: {lb['State']['Code']}")
        except Exception:
            pass

        # RDS Databases
        try:
            rds = boto3.client("rds", region_name=region)
            dbs = rds.describe_db_instances()
            for db in dbs['DBInstances']:
                print(f"RDS: {db['DBInstanceIdentifier']} | Engine: {db['Engine']} | AZ: {db['AvailabilityZone']}")
        except Exception:
            pass

        # ElastiCache
        try:
            elasticache = boto3.client("elasticache", region_name=region)
            clusters = elasticache.describe_cache_clusters(ShowCacheNodeInfo=True)
            for c in clusters['CacheClusters']:
                print(f"ElastiCache: {c['CacheClusterId']} | Engine: {c['Engine']} | Status: {c['CacheClusterStatus']}")
        except Exception:
            pass

        # DynamoDB (regional)
        try:
            dynamo = boto3.client("dynamodb", region_name=region)
            tables = dynamo.list_tables()
            for t in tables['TableNames']:
                print(f"DynamoDB Table: {t}")
        except Exception:
            pass

        # NAT Gateways
        try:
            ngws = ec2.describe_nat_gateways()
            for n in ngws['NatGateways']:
                print(f"NAT Gateway: {n['NatGatewayId']} | State: {n['State']} | Subnet: {n['SubnetId']}")
        except Exception:
            pass

        print()

    # ---------- Global Services ----------
    print("--- Global Services ---")

    # S3 Buckets
    try:
        s3 = boto3.client("s3")
        buckets = s3.list_buckets()
        for b in buckets['Buckets']:
            print(f"S3 Bucket: {b['Name']}")
    except Exception:
        pass

    # CloudFront
    try:
        cloudfront = boto3.client("cloudfront")
        dists = cloudfront.list_distributions()
        for d in dists.get("DistributionList", {}).get("Items", []):
            print(f"CloudFront: {d['Id']} | Domain: {d['DomainName']}")
    except Exception:
        pass

    # EKS (example region)
    try:
        eks = boto3.client("eks", region_name="us-east-1")
        clusters = eks.list_clusters()
        for c in clusters.get('clusters', []):
            print(f"EKS Cluster: {c}")
    except Exception:
        pass


if __name__ == "__main__":
    list_resources()
