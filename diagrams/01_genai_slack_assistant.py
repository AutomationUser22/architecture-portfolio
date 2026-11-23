from diagrams import Diagram, Cluster, Edge
from diagrams.saas.chat import Slack
from diagrams.aws.network import APIGateway
from diagrams.aws.security import WAF, KMS, SecretsManager
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import SQS, EventbridgeScheduler
from diagrams.aws.database import DynamodbTable
from diagrams.aws.ml import Bedrock
from diagrams.aws.management import Cloudwatch, CloudwatchAlarm
from diagrams.aws.devtools import Codepipeline
from diagrams.onprem.compute import Server
from diagrams.onprem.client import Users
from _style import *

with Diagram("", filename=out("01-genai-slack-assistant"), show=False, direction="LR",
             graph_attr=graph(label=title("Enterprise GenAI Slack Knowledge Assistant",
                 "Captures answers already given in Slack, governs them in team-owned knowledge bases, and answers repeat questions in-thread")),
             node_attr=NODE, edge_attr=EDGE):

    with Cluster("Slack (external)", graph_attr=EXTERNAL):
        slack = Slack("Slack workspace\nevents · slash commands ·\nreactions · interactivity")

    with Cluster("AWS Cloud · one account per stage (beta · gamma · prod)", graph_attr=CLOUD):
        with Cluster("Edge security", graph_attr=SECURITY):
            waf = WAF("AWS WAF")
            api = APIGateway("API Gateway\ncustom domain\nmutual TLS")
            certauth = Lambda("Lambda authorizer\nclient-certificate\ncheck")

        with Cluster("VPC · private subnets · VPC endpoints", graph_attr=VPC):
            receiver = Lambda("Lambda · Receiver\nverify request signature\nack < 3 s · drop retries")
            q = SQS("Amazon SQS\ninteractive + batch\nqueues")
            dlq = SQS("Dead-letter\nqueues")
            proc = Lambda("Lambda · Processor\ncapture · auto-answer ·\n@mention · feedback")

        with Cluster("Amazon Bedrock", graph_attr=AI):
            guard = Bedrock("Pinned guardrail version\n+ tiered models\nsmall: question detection\nstrong: Q&A extraction\nembeddings: semantic match")

        with Cluster("Amazon DynamoDB · encrypted with customer-managed KMS key", graph_attr=DATA):
            t_kb = DynamodbTable("Knowledge bases\n& approved entries")
            t_bind = DynamodbTable("Channel bindings\n& idempotency state")
            t_audit = DynamodbTable("Governance\naudit trail")
            t_cap = DynamodbTable("Model-interaction\ncapture (TTL)")

        with Cluster("Scheduled jobs", graph_attr=GROUP):
            sched = EventbridgeScheduler("EventBridge\nScheduler")
            rot = Lambda("Token rotator")
            pub = Lambda("Wiki publisher")
            sweep = Lambda("Cleanup sweeps")
            sec = SecretsManager("Secrets Manager\nSlack OAuth tokens")

        with Cluster("Operate", graph_attr=GROUP):
            cw = Cloudwatch("CloudWatch\ndashboards · funnels ·\nmodel-token spend")
            alarm = CloudwatchAlarm("Alarms → tickets\nby severity,\neach linked to a runbook")

    with Cluster("Delivery", graph_attr=GROUP):
        cd = Codepipeline("CodePipeline + AWS CDK\nbeta → gamma → prod\nbake time · auto-rollback")

    with Cluster("Enterprise services (external)", graph_attr=EXTERNAL):
        authz = Server("Directory / group\nmembership service\n(editor check on every write)")
        wiki = Server("Internal wiki\nper-KB pages,\nKB-scoped access")

    editors = Users("KB editors\napprove every entry")

    inv = {"style": "invis"}
    slack >> main(1, "HTTPS + client cert") >> waf >> api >> certauth
    certauth >> main(2, "verified") >> receiver
    receiver >> main(3, "enqueue") >> q >> main(4) >> proc
    proc >> async_(text="failed after retries") >> dlq
    proc >> main(5, "authorize") >> authz
    proc >> main(6, "extract / match") >> guard
    proc >> main(7, "conditional write") >> t_kb
    proc >> Edge(**inv) >> t_bind
    t_kb >> Edge(**inv) >> t_audit
    t_bind >> Edge(**inv) >> t_cap
    proc >> free(main, n=8, text="threaded reply") >> slack
    editors >> free(async_, text="Save · Amend · Discard") >> slack
    certauth >> Edge(**inv) >> sched
    sched >> async_() >> [rot, pub, sweep]
    rot >> async_() >> sec
    pub >> async_(text="publish") >> wiki
    proc >> obs() >> cw
    cw >> obs() >> alarm
