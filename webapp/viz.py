from .sheets import write_to_sheet, get_sheet_data, submit_to_survey, get_schools
from .utils import encrypt_string
import json
import numpy
import plotly.graph_objects as go
import networkx as nx


def gen_network(data):
    ids = set([d["Name"] for d in data])

    G = nx.Graph()
    for d in data:
        color = "cornflowerblue"
        if d.get("Vape", "False") == "True":
            color = "crimson"
        gender = d.get("Gender", None)
        if gender == "Male":
            symbol = "square"
        elif gender == "Female":
            symbol = "diamond"
        else:
            symbol = "circle"
        G.add_node(
            d["Name"],
            size=4,
            symbol=symbol,
            color=color,
            label=f"""
            <br>Id: {d["Name"][:10]}</br>
            <br>Influence: {d["Influence"]}</br>
            <br>Gender: {d["Gender"]}</br>
            <extra></extra>
            """,
        )
        friends = [
            d.get("Closest 1", None).lower(),
            d.get("Closest 2", None).lower(),
            d.get("Closest 3", None).lower(),
        ]
        for f in friends:
            skip_list = [encrypt_string(s) for s in ["", "n/a", "N/A"]]
            if f in skip_list:
                print(f, "skipped")
                continue
            if f not in ids:
                G.add_node(
                    f,
                    size=4,
                    color="white",
                    label=f"""
                    <br>Id: {f[:10]}</br>
                    <extra></extra>
                    """,
                    symbol="circle",
                )
                ids.add(f)
    # Add Edges
    for d in data:
        friends = [
            d.get("Closest 1", None).lower(),
            d.get("Closest 2", None).lower(),
            d.get("Closest 3", None).lower(),
        ]
        for f in friends:
            if f in ids:
                G.add_edge(d["Name"], f)

    pos_ = nx.spring_layout(G, seed=12)

    def make_edge(x, y, text, width):
        return go.Scatter(
            x=x,
            y=y,
            line=dict(width=width, color="cornflowerblue"),
            hoverinfo="text",
            text=([text]),
            mode="lines",
        )

    edge_trace = []
    for edge in G.edges():
        char_1 = edge[0]
        char_2 = edge[1]
        x0, y0 = pos_[char_1]
        x1, y1 = pos_[char_2]
        text = char_1 + "--" + char_2
        trace = make_edge(
            [x0, x1, None],
            [y0, y1, None],
            text,
            width=0.3,
        )
        edge_trace.append(trace)

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        textposition="top center",
        textfont_size=10,
        mode="markers+text",
        hoverinfo="none",
        hovertemplate=[],
        marker=dict(color=[], size=[], line=None),
        marker_symbol=[],
    )
    for node in G.nodes():
        x, y = pos_[node]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
        node_trace["marker"]["color"] += tuple([G.nodes()[node]["color"]])
        node_trace["marker"]["symbol"] += tuple([G.nodes()[node]["symbol"]])
        node_trace["marker"]["size"] += tuple([5 * G.nodes()[node]["size"]])
        # node_trace["text"] += tuple(["<b>" + node + "</b>"])
        node_trace["text"] += tuple([""])
        node_trace["hovertemplate"] += tuple([G.nodes()[node]["label"]])

    fig = go.Figure(
        data=edge_trace + [node_trace],
        layout=go.Layout(
            title="",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    return fig.to_plotly_json()
