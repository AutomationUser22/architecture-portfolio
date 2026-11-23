from diagrams import Diagram, Cluster, Edge
from diagrams.generic.device import Mobile
from diagrams.programming.framework import Vercel, Nextjs
from diagrams.onprem.compute import Server
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.database import Postgresql
from diagrams.onprem.monitoring import Sentry
from diagrams.onprem.client import Users
from _style import *

with Diagram("", filename=out("04-fitbuddy-ai"), show=False, direction="LR",
             graph_attr=graph(label=title("FitBuddy AI · Conversational Health Coach",
                 "React Native app with LLM meal logging and coaching personas · serverless API keeps keys and prompts off the device")),
             node_attr=NODE, edge_attr=EDGE):
    users = Users("Users\niOS · Android")
    with Cluster("Client", graph_attr=GROUP):
        app = Mobile("React Native / Expo\nchat · calorie ring ·\ndesk exercises · offline mode\nOTA updates")
    with Cluster("Vercel · serverless functions", graph_attr=CLOUD):
        chat = Vercel("/api/chat\npersona prompts ·\nevent extraction")
        meal = Vercel("/api/parse-meal\nnatural-language\nmeal → macros")
    with Cluster("Supabase", graph_attr=DATA):
        auth = Server("Auth · Google sign-in\nJWT signing keys (JWKS)")
        db = Postgresql("Postgres\nusers · logs ·\nUSDA-seeded food DB ·\nmacro cache")
    with Cluster("Upstash", graph_attr=GROUP):
        redis = Redis("Redis\ndaily quota\nfree 10 · pro 150")
    with Cluster("LLM provider", graph_attr=AI):
        llm = Server("OpenAI API\nsmall fast model ·\nstructured JSON")
    with Cluster("App services (third-party)", graph_attr=EXTERNAL):
        rc = Server("RevenueCat\nsubscriptions")
        push = Server("Expo push\nmove reminders")
        sentry = Sentry("Sentry\ncrash reporting")
    with Cluster("Web", graph_attr=GROUP):
        site = Nextjs("Next.js site\nSEO landing pages")

    users >> main(1, "message") >> app >> main(2, "request with JWT  ·  7 reply + extracted events", dir="both") >> chat
    app >> meal
    chat >> main(3, "verify JWT") >> auth
    chat >> main(4, "quota") >> redis
    meal >> main(5, "cache / food DB") >> db
    chat >> main(6, "prompt") >> llm
    meal >> llm
    app >> async_() >> rc
    app >> async_() >> push
    app >> obs() >> sentry
    users >> free(async_) >> site
