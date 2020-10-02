import logging

from aws_cdk import (
    aws_ec2,
    aws_ecs,
    aws_ecs_patterns,
    aws_servicediscovery,
    aws_iam,
    aws_sqs,
    aws_ecr,
    core,
)

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


# Creating a construct that will populate the required objects created in the platform repo such as vpc, ecs cluster, and service discovery namespace
class BasePlatform(core.Construct):
    def __init__(self, scope: core.Construct, id: str, stage: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        # self.environment_name = "nlp"

        # The base platform stack is where the VPC was created, so all we need is the name to do a lookup and import it into this stack for use
        self.vpc = aws_ec2.Vpc.from_lookup(
            self, "VPC{}".format(stage), vpc_name=stage.lower()
        )

        self.sd_namespace = aws_servicediscovery.PrivateDnsNamespace.from_private_dns_namespace_attributes(
            self,
            "SDNamespace",
            namespace_name=core.Fn.import_value("NSNAME{}".format(stage)),
            namespace_arn=core.Fn.import_value("NSARN{}".format(stage)),
            namespace_id=core.Fn.import_value("NSID{}".format(stage)),
        )

        self.ecs_cluster = aws_ecs.Cluster.from_cluster_attributes(
            self,
            "ECSCluster{}".format(stage),
            cluster_name=core.Fn.import_value("ECSClusterName{}".format(stage)),
            security_groups=[],
            vpc=self.vpc,
            default_cloud_map_namespace=self.sd_namespace,
        )

        # self.services_sec_grp = aws_ec2.SecurityGroup.from_security_group_id(
        #     self,
        #     "ServicesSecGrp",
        #     security_group_id=core.Fn.import_value("ServicesSecGrp{}".format(stage)),
        # )


class ServiceStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str, stage: str, config: dict, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.base_platform = BasePlatform(self, self.stack_name, stage)

        self.ecr_repo = aws_ecr.Repository(
            self, "{}-ecr".format(self.stack_name), repository_name=self.stack_name
        )

        self.queue = aws_sqs.Queue(self, "{}-queue".format(self.stack_name))

        self.dlqueue = aws_sqs.DeadLetterQueue(max_receive_count=5, queue=self.queue)

        # Create QueueProcessingEc2Service
        self.ecs_service = aws_ecs_patterns.QueueProcessingEc2Service(
            self,
            "{}-svc".format(self.stack_name),
            cluster=self.base_platform.ecs_cluster,
            family=self.stack_name,
            service_name=self.stack_name,
            image=aws_ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            desired_task_count=0,
            max_scaling_capacity=10,
            memory_reservation_mib=1024,
            cpu=512,
            scaling_steps=[
                {"upper": 0, "change": -1},
                {"lower": 1, "change": +1},
                {"lower": 500, "change": +5},
            ],
            queue=self.queue,
        )
