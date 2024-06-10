import boto3
import csv
import argparse

def get_all_regions():
    # Initialize boto3 client for EC2
    ec2_client = boto3.client('ec2')
    
    # Describe all regions
    response = ec2_client.describe_regions()
    
    # Extract region names
    regions = [region['RegionName'] for region in response['Regions']]
    
    return regions

def get_vpcs_info(region):
    # Initialize boto3 client for EC2 in the specified region
    ec2_client = boto3.client('ec2', region_name=region)
    
    # Describe VPCs
    response = ec2_client.describe_vpcs()
    
    # Extract VPC information, excluding default VPCs
    vpcs_info = []
    for vpc in response['Vpcs']:
        if vpc.get('IsDefault'):
            continue
        
        vpc_id = vpc['VpcId']
        vpc_cidr = vpc['CidrBlock']
        
        # Get VPC name from tags if available
        vpc_name = None
        if 'Tags' in vpc:
            for tag in vpc['Tags']:
                if tag['Key'] == 'Name':
                    vpc_name = tag['Value']
                    break
        
        vpcs_info.append({
            'VPC Name': vpc_name,
            'VPC CIDR': vpc_cidr,
            'VPC ID': vpc_id,
            'Region': region
        })
    
    return vpcs_info

def print_vpcs_info(vpcs_info):
    print(f"{'VPC Name':<20} {'VPC CIDR':<20} {'VPC ID':<20} {'Region'}")
    print("="*80)
    for vpc in vpcs_info:
        print(f"{vpc['VPC Name']:<20} {vpc['VPC CIDR']:<20} {vpc['VPC ID']:<20} {vpc['Region']}")

def save_to_csv(vpcs_info, filename='vpcs_info.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['VPC Name', 'VPC CIDR', 'VPC ID', 'Region'])
        writer.writeheader()
        for vpc in vpcs_info:
            writer.writerow(vpc)

def main(account_number, regions):
    if 'all' in regions:
        regions = get_all_regions()
    
    # Print the account number and regions
    print(f"Fetching VPC information for AWS Account: {account_number} in regions: {', '.join(regions)}")
    
    all_vpcs_info = []
    for region in regions:
        vpcs_info = get_vpcs_info(region)
        all_vpcs_info.extend(vpcs_info)
    
    print_vpcs_info(all_vpcs_info)
    save_to_csv(all_vpcs_info, filename=f'vpcs_info_{account_number}.csv')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and list VPC information for a given AWS account.')
    parser.add_argument('account_number', type=str, help='AWS account number')
    parser.add_argument('regions', type=str, nargs='+', help='AWS regions to check for VPCs (use "all" for all regions)')
    
    args = parser.parse_args()
    main(args.account_number, args.regions)
