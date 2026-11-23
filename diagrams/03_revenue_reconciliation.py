from diagrams import Diagram, Cluster, Edge
from diagrams.aws.database import Redshift
from diagrams.aws.storage import S3
from diagrams.aws.analytics import Glue, Quicksight, GlueDataCatalog
from diagrams.aws.devtools import Codepipeline
from diagrams.aws.management import CloudwatchLogs
from diagrams.onprem.analytics import Spark
from diagrams.onprem.client import User
from _style import *

with Diagram("", filename=out("03-revenue-reconciliation"), show=False, direction="LR",
             graph_attr=graph(label=title("Revenue Reconciliation Data Pipeline",
                 "Reconciles tax-engine transactions against the accounting ledger at hundreds of millions of rows a month · match rate 53% → 96.5%")),
             node_attr=NODE, edge_attr=EDGE):
    with Cluster("AWS Cloud", graph_attr=CLOUD):
        with Cluster("Amazon Redshift · sources", graph_attr=DATA):
            tax = Redshift("Tax-engine\ntransactions")
            ledger = Redshift("Accounting\nledger")
        with Cluster("Amazon S3 · data lake (Parquet)", graph_attr=GROUP):
            raw = S3("Raw extracts\npartitioned by period")
            cat = GlueDataCatalog("Glue Data Catalog")
        with Cluster("AWS Glue · transform", graph_attr=AI):
            join = Glue("Join-key rules\norder · digital ·\nsubscription")
            spark = Spark("PySpark\nFX conversion ·\nscoped business rules ·\nknown-issue classes")
            agg = Glue("Aggregate +\nreconciliation status")
        with Cluster("Amazon S3 · curated", graph_attr=GROUP):
            cur = S3("Joined &\naggregated Parquet")
        with Cluster("Serve", graph_attr=DATA):
            recon = Redshift("Redshift\nreconciliation tables")
            dash = Quicksight("QuickSight dashboards\nmatched · missing ·\nknown issue")
        with Cluster("Delivery & operate", graph_attr=GROUP):
            cd = Codepipeline("CodePipeline + AWS CDK\nautomated approval\n(replaced manual gate)")
            logs = CloudwatchLogs("CloudWatch Logs\njob runs")
    analyst = User("Engineer / analyst\nroot-cause loop")

    tax >> main(1, "UNLOAD") >> raw
    ledger >> main(1, "UNLOAD") >> raw
    raw >> main(2) >> join >> main(3) >> spark >> main(4) >> agg >> main(5) >> cur >> main(6, "COPY") >> recon >> main(7) >> dash
    raw - Edge(color="#A0A8B3") - cat
    dash >> free(async_, text="largest unmatched class") >> analyst
    analyst >> free(async_, text="new scoped rule") >> spark
    agg >> obs() >> logs
    cd >> free(async_, text="deploys") >> join
