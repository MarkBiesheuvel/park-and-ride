#!/usr/bin/env python3
from constructs import Construct
from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
)


class Website(Construct):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Determine domain name and sub domain from the context variables
        domain_name = self.node.try_get_context('domainName')
        subdomain = 'park-and-ride.{}'.format(domain_name)

        # Assumption: Hosted Zone is created outside of this project
        # Fetch the Route53 Hosted Zone
        zone = route53.HostedZone.from_lookup(
            self, 'Zone',
            domain_name=domain_name,
        )

        # Bucket to store static website files, such as HTML and JavaScript
        bucket = s3.Bucket(self, 'Storage')

        # Copy local files to S3
        s3_deployment.BucketDeployment(
            self, 'Deployment',
            sources=[
                s3_deployment.Source.asset('./src/html'),
            ],
            destination_bucket=bucket,
        )

        # Give a CloudFront OAI access to the S3 bucket
        origin_identity = cloudfront.OriginAccessIdentity(self, 'Identity')
        bucket.grant_read(origin_identity.grant_principal)

        # S3 Origin
        default_behavior = cloudfront.BehaviorOptions(
            origin=origins.S3Origin(
                bucket=bucket,
                origin_access_identity=origin_identity,
            ),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
        )

        # Public SSL certificate for subdomain
        certificate = acm.DnsValidatedCertificate(
            self, 'Certificate',
            domain_name=subdomain,
            hosted_zone=zone,
            region='us-east-1',
        )

        # Content Delivery Network
        distribution = cloudfront.Distribution(
            self, 'CDN',
            default_root_object='index.html',
            domain_names=[subdomain],
            certificate=certificate,
            default_behavior=default_behavior
        )

        # Both IPv4 and IPv6 addresses
        target = route53.RecordTarget.from_alias(
            alias_target=targets.CloudFrontTarget(distribution)
        )
        route53.AaaaRecord(
            self, 'DnsRecordIpv6',
            record_name=subdomain,
            target=target,
            zone=zone,
        )
        route53.ARecord(
            self, 'DnsRecordIpv4',
            record_name=subdomain,
            target=target,
            zone=zone,
        )