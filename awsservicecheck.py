import boto3

def get_regions():
ec2 = boto3.client("ec2")
return [r['RegionName'] for r in ec2.describe_regions()['Regions']]

def list_resources():
regions = get_regions()
print("==== AWS Payable Resources Across All Regions ====\n")

for region in regions:
print(f"--- Region: {region} ---")

# EC2 Instances
ec2 = boto3.client("ec2", region_name=region)
instances = ec2.describe_instances()
for r in instances['Reservations']:
for i in r['Instances']:
print(f"EC2: {i['InstanceId']} | Type: {i['InstanceType']} | State: {i['State']['Name']} | AZ: {i['Placement']['AvailabilityZone']}")

# EBS Volumes
volumes = ec2.describe_volumes()
for v in volumes['Volumes']:
print(f"EBS Volume: {v['VolumeId']} | Size: {v['Size']} GiB | State: {v['State']}")

# Elastic IPs
eips = ec2.describe_addresses()
for e in eips['Addresses']:
print(f"Elastic IP: {e.get('PublicIp')} | Instance: {e.get('InstanceId')}")

# Load Balancers
elb = boto3.client("elbv2", region_name=region)
try:
lbs = elb.describe_load_balancers()
for lb in lbs['LoadBalancers']:
print(f"LoadBalancer: {lb['LoadBalancerName']} | Type: {lb['Type']} | State: {lb['State']['Code']}")
except:
pass

# RDS Databases
rds = boto3.client("rds", region_name=region)
try:
dbs = rds.describe_db_instances()
for db in dbs['DBInstances']:
print(f"RDS: {db['DBInstanceIdentifier']} | Engine: {db['Engine']} | AZ: {db['AvailabilityZone']}")
except:
pass

# ElastiCache
elasticache = boto3.client("elasticache", region_name=region)
try:
clusters = elasticache.describe_cache_clusters(ShowCacheNodeInfo=True)
for c in clusters['CacheClusters']:
print(f"ElastiCache: {c['CacheClusterId']} | Engine: {c['Engine']} | Status: {c['CacheClusterStatus']}")
except:
pass

# DynamoDB (regional, but billing depends on usage)
dynamo = boto3.client("dynamodb", region_name=region)
try:
tables = dynamo.list_tables()
for t in tables['TableNames']:
print(f"DynamoDB Table: {t}")
except:
pass

# NAT Gateways
try:
ngws = ec2.describe_nat_gateways()
for n in ngws['NatGateways']:
print(f"NAT Gateway: {n['NatGatewayId']} | State: {n['State']} | Subnet: {n['SubnetId']}")
except:
pass

print()

# Global services (S3, CloudFront, EKS)
print("--- Global Services ---")
s3 = boto3.client("s3")
buckets = s3.list_buckets()
for b in buckets['Buckets']:
print(f"S3 Bucket: {b['Name']}")

cloudfront = boto3.client("cloudfront")
dists = cloudfront.list_distributions()
for d in dists.get("DistributionList", {}).get("Items", []):
print(f"CloudFront: {d['Id']} | Domain: {d['DomainName']}")

eks = boto3.client("eks", region_name="us-east-1") # EKS is regional, but list per region if needed
try:
clusters = eks.list_clusters()
for c in clusters['clusters']:
print(f"EKS Cluster: {c}")
except:
pass


if __name__ == "__main__":
list_resources()
