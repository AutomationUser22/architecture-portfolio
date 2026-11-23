from diagrams import Diagram, Cluster, Edge
from diagrams.generic.os import Android
from diagrams.programming.language import Kotlin
from diagrams.generic.database import SQL
from diagrams.firebase.develop import Authentication, Firestore, Functions
from diagrams.firebase.quality import Crashlytics
from diagrams.gcp.analytics import Pubsub
from diagrams.onprem.compute import Server
from diagrams.programming.framework import Nextjs
from _style import *

inv = {"style": "invis"}
with Diagram("", filename=out("05-streakly-android"), show=False, direction="LR",
             graph_attr=graph(label=title("Streakly · Android Habit Tracker",
                 "Offline-first clean architecture in Kotlin · Firestore sync · server-verified subscriptions")),
             node_attr=NODE, edge_attr=EDGE):
    with Cluster("Android app · Kotlin · Hilt dependency injection", graph_attr=CLOUD):
        with Cluster("UI layer", graph_attr=GROUP):
            ui = Android("Jetpack Compose\n+ Glance widget")
            vm = Kotlin("ViewModels\nStateFlow")
        with Cluster("Domain layer", graph_attr=GROUP):
            dom = Kotlin("Streak calculator ·\nstats · repository\ninterfaces")
        with Cluster("Data layer", graph_attr=DATA):
            repo = Kotlin("Repository\nimplementations")
            room = SQL("Room\nversioned schema")
            ds = SQL("DataStore\npreferences")
        with Cluster("Background", graph_attr=GROUP):
            wm = Kotlin("WorkManager\nadaptive reminders ·\nstreak-at-risk ·\nweekly review")
    with Cluster("Firebase", graph_attr=AI):
        fauth = Authentication("Auth\nCredential Manager\nGoogle sign-in")
        fs = Firestore("Firestore\ncloud sync")
        fn = Functions("Cloud Functions\nverifyPurchase (App Check) ·\nRTDN handler")
        crash = Crashlytics("Crashlytics · Analytics\nApp Check (Play Integrity)")
    with Cluster("Google Play", graph_attr=EXTERNAL):
        billing = Server("Play Billing")
        rtdn = Pubsub("Real-time developer\nnotifications (Pub/Sub)")

    ui >> main(1) >> vm >> main(2) >> dom >> main(3) >> repo >> main(4, "offline-first") >> room
    repo >> ds
    repo >> main(5, "sync") >> fs
    wm >> free(async_) >> repo
    vm >> Edge(label="sign-in") >> fauth
    ui >> async_(text="purchase") >> billing
    billing >> free(async_, text="token") >> fn
    rtdn >> async_(text="renewals · refunds") >> fn
    fn >> async_(text="entitlement") >> fs
    ui >> obs() >> crash
