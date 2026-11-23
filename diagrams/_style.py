"""Shared visual language for every diagram in the portfolio."""
from diagrams import Edge
from html import escape as _e

INK, MUTED, ORANGE = "#232F3E", "#5F6B7A", "#FF9900"

def out(name): return f"../img/{name}"

def title(name, subtitle):
    name, subtitle = _e(name, False), _e(subtitle, False)
    return (f'<<FONT POINT-SIZE="28" COLOR="{INK}"><B>{name}</B></FONT><BR/>'
            f'<FONT POINT-SIZE="15" COLOR="{MUTED}">{subtitle}</FONT><BR/>'
            f'<FONT POINT-SIZE="12" COLOR="{MUTED}">'
            f'<FONT COLOR="{ORANGE}"><B>&#9679;</B></FONT> numbered steps = main flow    '
            f'solid = synchronous    dashed = asynchronous / background    dotted = monitoring</FONT><BR/> >')

def graph(**over):
    g = {"fontname": "Helvetica", "bgcolor": "white", "pad": "0.6", "nodesep": "0.55",
         "ranksep": "0.95", "splines": "spline", "newrank": "true", "labelloc": "t",
         "fontcolor": INK}
    g.update(over); return g

NODE = {"fontsize": "13", "fontname": "Helvetica", "fontcolor": INK}
EDGE = {"fontsize": "11", "fontname": "Helvetica", "color": "#545B64", "penwidth": "1.4",
        "arrowsize": "0.8"}

def _c(pen, fill="#FFFFFF", style="rounded", width="1.6"):
    return {"pencolor": pen, "bgcolor": fill, "style": style, "penwidth": width,
            "fontcolor": INK, "fontsize": "14", "fontname": "Helvetica-Bold", "labeljust": "l",
            "margin": "18"}

CLOUD = _c(INK, "#FFFFFF", "rounded", "2")              # AWS Cloud / platform boundary
ACCOUNT = _c("#E7157B", "#FFFFFF", "rounded,dashed")     # account / stage boundary
VPC = _c("#8C4FFF", "#FBF8FF")                           # VPC
GROUP = _c("#7D8998", "#F7F9FA", "rounded,dashed", "1.2")  # logical group
SECURITY = _c("#DD344C", "#FFF7F8", "rounded", "1.4")    # security boundary
AI = _c("#01A88D", "#F2FBF9", "rounded", "1.4")          # GenAI
DATA = _c("#4D27AA", "#F7F5FD", "rounded", "1.4")        # data stores
EXTERNAL = _c("#545B64", "#FFFFFF", "rounded,dotted", "1.2")  # third party / outside

def step(n, text=""):
    text = _e(str(text), False)
    txt = (f'<TD><FONT POINT-SIZE="11" COLOR="{INK}"> {text}</FONT></TD>') if text else ''
    return (f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="2"><TR>'
            f'<TD BGCOLOR="{ORANGE}" STYLE="rounded"><FONT COLOR="white" POINT-SIZE="12"><B> {n} </B></FONT></TD>'
            f'{txt}</TR></TABLE>>')

def main(n=None, text="", **kw):
    return Edge(label=step(n, text) if n is not None else text, color=INK, penwidth="1.8", **kw)

def async_(text="", **kw):
    return Edge(label=text, style="dashed", color="#7D8998", **kw)

def obs(text="", **kw):
    return Edge(label=text, style="dotted", color="#A0A8B3", **kw)

def free(edge_fn=async_, **kw):
    """Edge that does not affect layout ranks."""
    return edge_fn(constraint="false", **kw)
