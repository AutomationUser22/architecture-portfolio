from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.programming.framework import React
from diagrams.onprem.database import Postgresql
from diagrams.onprem.compute import Server
from diagrams.generic.database import SQL
from diagrams.aws.integration import EventbridgeScheduler
from _style import *

with Diagram("", filename=out("06-household-networth"), show=False, direction="LR",
             graph_attr=graph(label=title("Household Net Worth · Multi-user Finance App",
                 "TypeScript full-stack app on Supabase · row-level security per household · live prices, FX and daily snapshots")),
             node_attr=NODE, edge_attr=EDGE):
    users = Users("Household members\ninvite link · 2FA")
    cron = EventbridgeScheduler("Scheduled cron\n(daily)")
    with Cluster("Web app · TanStack Start (TypeScript) · Vitest suites", graph_attr=CLOUD):
        ui = React("React UI\nTanStack Router + Query\nreact-hook-form + Zod")
        job = Server("Daily-snapshot job\nBearer secret,\nrotation-ready")
        srv = Server("Server functions\npricing · XIRR ·\ntax classification")
    with Cluster("Supabase", graph_attr=DATA):
        auth = Server("Auth\nemail + 2FA")
        with Cluster("Postgres · row-level security · 11 Drizzle migrations", graph_attr=SECURITY):
            db = Postgresql("Households · assets (lots) ·\nliabilities (principal / interest)\n· goals · snapshots · tax centre")
            cache = SQL("Price & FX caches\nrestricted reads")
    with Cluster("Market data (external)", graph_attr=EXTERNAL):
        mkt = Server("Yahoo Finance · Finnhub\nmfapi.in (Indian funds)\nFrankfurter (FX)")

    users >> main(1) >> ui >> main(2, "session") >> auth
    ui >> main(3, "queries under RLS") >> db
    ui >> main(4) >> srv >> main(5, "fetch") >> mkt
    srv >> main(6, "write") >> cache
    cron >> async_(text="daily") >> job >> async_(text="snapshot each household") >> db
