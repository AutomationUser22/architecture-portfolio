from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import S3
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamodbTable
from diagrams.aws.integration import EventbridgeScheduler
from diagrams.aws.engagement import SES
from diagrams.aws.management import Cloudformation
from diagrams.onprem.client import User
from _style import *

with Diagram("", filename=out("07-aws-serverless-pipeline"), show=False, direction="LR",
             graph_attr=graph(label=title("Event-driven Data Pipeline on AWS",
                 "Open source · CSV → validated Parquet with idempotent ingestion, quarantine and daily reports · infrastructure in AWS CDK")),
             node_attr=NODE, edge_attr=EDGE):
    user = User("CSV upload")
    with Cluster("AWS Cloud · deployed with AWS CDK (TypeScript)", graph_attr=CLOUD):
        raw = S3("S3 · raw/")
        ingest = Lambda("Lambda · Ingest\nschema check · cleanse ·\nCSV → Parquet")
        with Cluster("Amazon S3 · outputs", graph_attr=GROUP):
            proc = S3("processed/\nParquet (Snappy)")
            quar = S3("quarantine/\ninvalid rows")
        ddb = DynamodbTable("DynamoDB\nfile ledger\n(SHA-256 → idempotency)")
        sched = EventbridgeScheduler("EventBridge\ndaily schedule")
        agg = Lambda("Lambda · Aggregate\n1 GB memory")
        rep = S3("S3 · reports/")
        report = Lambda("Lambda · Report")
        ses = SES("Amazon SES")
    inbox = User("Stakeholders")

    user >> main(1) >> raw >> main(2, "PutObject event") >> ingest
    ingest >> main(3, "seen before?") >> ddb
    ingest >> main(4) >> proc
    ingest >> async_(text="bad rows") >> quar
    sched >> main(5) >> agg
    proc >> async_(text="reads Parquet") >> agg
    agg >> main(6) >> rep >> main(7) >> report >> main(8) >> ses >> inbox
