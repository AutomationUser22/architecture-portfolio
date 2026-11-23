from diagrams import Diagram, Cluster, Edge
from diagrams.aws.engagement import SES
from diagrams.aws.storage import S3
from diagrams.aws.integration import Eventbridge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamodbTable, DynamodbStreams
from diagrams.aws.ml import Bedrock
from diagrams.aws.network import APIGateway
from diagrams.aws.management import Cloudwatch
from diagrams.aws.devtools import Codepipeline
from diagrams.onprem.client import Users
from diagrams.programming.framework import React
from diagrams.saas.chat import Slack
from _style import *

inv = {"style": "invis"}
with Diagram("", filename=out("02-email-kb-rag-platform"), show=False, direction="LR",
             graph_attr=graph(label=title("Multi-tenant Email-to-Knowledge-Base RAG Platform",
                 "Turns team mailboxes into per-tenant Bedrock Knowledge Bases, with self-service onboarding and a Slack Q&A assistant")),
             node_attr=NODE, edge_attr=EDGE):
    senders = Users("Team mailboxes\nallowlisted senders")
    admins = Users("Program owners")
    with Cluster("Slack (external)", graph_attr=EXTERNAL):
        slack = Slack("@mention in a thread")

    with Cluster("AWS Cloud · beta and prod stages", graph_attr=CLOUD):
        with Cluster("Ingestion", graph_attr=GROUP):
            ses = SES("Amazon SES\nreceipt rule")
            raw = S3("S3 · raw MIME\nencrypted · random keys")
            bus = Eventbridge("EventBridge\nObject Created")
            parser = Lambda("Lambda · Parser\nMIME + attachments →\nmarkdown + metadata")

        with Cluster("Per-tenant knowledge", graph_attr=AI):
            tenant = S3("S3 · tenant bucket\n(one per program)")
            kb = Bedrock("Bedrock Knowledge Base\nS3 Vectors")

        with Cluster("Conversational Q&A", graph_attr=AI):
            handler = Lambda("Lambda · Slack handler\nthreaded sessions")
            llm = Bedrock("RetrieveAndGenerate\nClaude via inference profile")
            sessions = DynamodbTable("DynamoDB · sessions\npoint-in-time recovery")

        with Cluster("Self-service control plane", graph_attr=GROUP):
            console = React("React console\nrequest · edit · refresh")
            api = APIGateway("API Gateway\nowner checks")
            apifn = Lambda("Lambda · API\nunique program name ·\nno recipient reuse")
            routes = DynamodbTable("DynamoDB · routes\n& programs")
            streams = DynamodbStreams("DynamoDB Streams")
            prov = Lambda("Lambda · Provisioner\ncreates bucket + KB\n~30 s (was ~1 day)")

        with Cluster("Operate", graph_attr=GROUP):
            cw = Cloudwatch("CloudWatch alarms\nKMS-encrypted logs")
            cd = Codepipeline("CodePipeline + CDK\nper-stage integration tests")

    senders >> main(1, "email") >> ses >> main(2) >> raw >> main(3) >> bus >> main(4) >> parser
    parser >> main(5, "write") >> tenant >> main(6, "ingest / sync") >> kb
    parser >> free(async_, text="route lookup") >> routes
    slack >> main("A", "question") >> handler >> main("B", "retrieve + generate") >> llm
    handler >> sessions
    llm >> free(async_, text="queries tenant KB") >> kb
    handler >> free(main, n="C", text="grounded answer + feedback") >> slack
    admins >> async_() >> console >> async_() >> api >> async_() >> apifn >> async_() >> routes >> async_() >> streams >> async_() >> prov
    prov >> free(async_, text="create bucket + KB") >> tenant
    kb >> Edge(**inv) >> cw
    kb >> Edge(**inv) >> cd
