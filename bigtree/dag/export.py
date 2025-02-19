from typing import Any, Dict, List, Tuple, Union

import pandas as pd

from bigtree.node.dagnode import DAGNode
from bigtree.utils.iterators import dag_iterator

__all__ = ["dag_to_list", "dag_to_dict", "dag_to_dataframe", "dag_to_dot"]


def dag_to_list(
    dag: DAGNode,
) -> List[Tuple[str, str]]:
    """Export DAG to list of tuple containing parent-child names

    >>> from bigtree import DAGNode, dag_to_list
    >>> a = DAGNode("a", step=1)
    >>> b = DAGNode("b", step=1)
    >>> c = DAGNode("c", step=2, parents=[a, b])
    >>> d = DAGNode("d", step=2, parents=[a, c])
    >>> e = DAGNode("e", step=3, parents=[d])
    >>> dag_to_list(a)
    [('a', 'c'), ('a', 'd'), ('b', 'c'), ('c', 'd'), ('d', 'e')]

    Args:
        dag (DAGNode): DAG to be exported

    Returns:
        (List[Tuple[str, str]])
    """
    relations = []
    for parent_node, child_node in dag_iterator(dag):
        relations.append((parent_node.node_name, child_node.node_name))
    return relations


def dag_to_dict(
    dag: DAGNode,
    parent_key: str = "parents",
    attr_dict: Dict[str, str] = {},
    all_attrs: bool = False,
) -> Dict[str, Any]:
    """Export tree to dictionary.

    Exported dictionary will have key as child name, and parent names and node attributes as a nested dictionary.

    >>> from bigtree import DAGNode, dag_to_dict
    >>> a = DAGNode("a", step=1)
    >>> b = DAGNode("b", step=1)
    >>> c = DAGNode("c", step=2, parents=[a, b])
    >>> d = DAGNode("d", step=2, parents=[a, c])
    >>> e = DAGNode("e", step=3, parents=[d])
    >>> dag_to_dict(a, parent_key="parent", attr_dict={"step": "step no."})
    {'a': {'step no.': 1}, 'c': {'parent': ['a', 'b'], 'step no.': 2}, 'd': {'parent': ['a', 'c'], 'step no.': 2}, 'b': {'step no.': 1}, 'e': {'parent': ['d'], 'step no.': 3}}

    Args:
        dag (DAGNode): DAG to be exported
        parent_key (str): dictionary key for `node.parent.node_name`, defaults to `parents`
        attr_dict (Dict[str, str]): dictionary mapping node attributes to dictionary key,
            key: node attributes, value: corresponding dictionary key, optional
        all_attrs (bool): indicator whether to retrieve all `Node` attributes, defaults to False

    Returns:
        (Dict[str, Any])
    """
    dag = dag.copy()
    data_dict = {}

    for parent_node, child_node in dag_iterator(dag):
        if parent_node.is_root:
            data_parent: Dict[str, Any] = {}
            if all_attrs:
                data_parent.update(
                    parent_node.describe(
                        exclude_attributes=["name"], exclude_prefix="_"
                    )
                )
            else:
                for k, v in attr_dict.items():
                    data_parent[v] = parent_node.get_attr(k)
            data_dict[parent_node.node_name] = data_parent

        if data_dict.get(child_node.node_name):
            data_dict[child_node.node_name][parent_key].append(parent_node.node_name)
        else:
            data_child = {parent_key: [parent_node.node_name]}
            if all_attrs:
                data_child.update(
                    child_node.describe(exclude_attributes=["name"], exclude_prefix="_")
                )
            else:
                for k, v in attr_dict.items():
                    data_child[v] = child_node.get_attr(k)
            data_dict[child_node.node_name] = data_child
    return data_dict


def dag_to_dataframe(
    dag: DAGNode,
    name_col: str = "name",
    parent_col: str = "parent",
    attr_dict: Dict[str, str] = {},
    all_attrs: bool = False,
) -> pd.DataFrame:
    """Export DAG to pandas DataFrame.

    >>> from bigtree import DAGNode, dag_to_dataframe
    >>> a = DAGNode("a", step=1)
    >>> b = DAGNode("b", step=1)
    >>> c = DAGNode("c", step=2, parents=[a, b])
    >>> d = DAGNode("d", step=2, parents=[a, c])
    >>> e = DAGNode("e", step=3, parents=[d])
    >>> dag_to_dataframe(a, name_col="name", parent_col="parent", attr_dict={"step": "step no."})
      name parent  step no.
    0    a   None         1
    1    c      a         2
    2    d      a         2
    3    b   None         1
    4    c      b         2
    5    d      c         2
    6    e      d         3

    Args:
        dag (DAGNode): DAG to be exported
        name_col (str): column name for `node.node_name`, defaults to 'name'
        parent_col (str): column name for `node.parent.node_name`, defaults to 'parent'
        attr_dict (Dict[str, str]): dictionary mapping node attributes to column name,
            key: node attributes, value: corresponding column in dataframe, optional
        all_attrs (bool): indicator whether to retrieve all `Node` attributes, defaults to False

    Returns:
        (pd.DataFrame)
    """
    dag = dag.copy()
    data_list: List[Dict[str, Any]] = []

    for parent_node, child_node in dag_iterator(dag):
        if parent_node.is_root:
            data_parent = {name_col: parent_node.node_name, parent_col: None}
            if all_attrs:
                data_parent.update(
                    parent_node.describe(
                        exclude_attributes=["name"], exclude_prefix="_"
                    )
                )
            else:
                for k, v in attr_dict.items():
                    data_parent[v] = parent_node.get_attr(k)
            data_list.append(data_parent)

        data_child = {name_col: child_node.node_name, parent_col: parent_node.node_name}
        if all_attrs:
            data_child.update(
                child_node.describe(exclude_attributes=["name"], exclude_prefix="_")
            )
        else:
            for k, v in attr_dict.items():
                data_child[v] = child_node.get_attr(k)
        data_list.append(data_child)
    return pd.DataFrame(data_list).drop_duplicates().reset_index(drop=True)


def dag_to_dot(  # type: ignore[no-untyped-def]
    dag: Union[DAGNode, List[DAGNode]],
    rankdir: str = "TB",
    bg_colour: str = "",
    node_colour: str = "",
    edge_colour: str = "",
    node_attr: str = "",
    edge_attr: str = "",
):
    r"""Export DAG tree or list of DAG trees to image.
    Note that node names must be unique.
    Posible node attributes include style, fillcolor, shape.

    >>> from bigtree import DAGNode, dag_to_dot
    >>> a = DAGNode("a", step=1)
    >>> b = DAGNode("b", step=1)
    >>> c = DAGNode("c", step=2, parents=[a, b])
    >>> d = DAGNode("d", step=2, parents=[a, c])
    >>> e = DAGNode("e", step=3, parents=[d])
    >>> dag_graph = dag_to_dot(a)

    Export to image, dot file, etc.

    >>> dag_graph.write_png("tree_dag.png")
    >>> dag_graph.write_dot("tree_dag.dot")

    Export to string

    >>> dag_graph.to_string()
    'strict digraph G {\nrankdir=TB;\nc [label=c];\na [label=a];\na -> c;\nd [label=d];\na [label=a];\na -> d;\nc [label=c];\nb [label=b];\nb -> c;\nd [label=d];\nc [label=c];\nc -> d;\ne [label=e];\nd [label=d];\nd -> e;\n}\n'

    Args:
        dag (Union[DAGNode, List[DAGNode]]): DAG or list of DAGs to be exported
        rankdir (str): set direction of graph layout, defaults to 'TB', can be 'BT, 'LR', 'RL'
        bg_colour (str): background color of image, defaults to ''
        node_colour (str): fill colour of nodes, defaults to ''
        edge_colour (str): colour of edges, defaults to ''
        node_attr (str): node attribute for style, overrides node_colour, defaults to ''
            Possible node attributes include {"style": "filled", "fillcolor": "gold"}
        edge_attr (str): edge attribute for style, overrides edge_colour, defaults to ''
            Possible edge attributes include {"style": "bold", "label": "edge label", "color": "black"}

    Returns:
        (pydot.Dot)
    """
    try:
        import pydot
    except ImportError:  # pragma: no cover
        raise ImportError(
            "pydot not available. Please perform a\n\npip install 'bigtree[image]'\n\nto install required dependencies"
        )

    # Get style
    if bg_colour:
        graph_style = dict(bgcolor=bg_colour)
    else:
        graph_style = dict()

    if node_colour:
        node_style = dict(style="filled", fillcolor=node_colour)
    else:
        node_style = dict()

    if edge_colour:
        edge_style = dict(color=edge_colour)
    else:
        edge_style = dict()

    _graph = pydot.Dot(
        graph_type="digraph", strict=True, rankdir=rankdir, **graph_style
    )

    if not isinstance(dag, list):
        dag = [dag]

    for _dag in dag:
        if not isinstance(_dag, DAGNode):
            raise ValueError(
                "Tree should be of type `DAGNode`, or inherit from `DAGNode`"
            )
        _dag = _dag.copy()

        for parent_node, child_node in dag_iterator(_dag):
            child_name = child_node.name
            child_node_style = node_style.copy()
            if node_attr and child_node.get_attr(node_attr):
                child_node_style.update(child_node.get_attr(node_attr))
            if edge_attr:
                edge_style.update(child_node.get_attr(edge_attr))
            pydot_child = pydot.Node(
                name=child_name, label=child_name, **child_node_style
            )
            _graph.add_node(pydot_child)

            parent_name = parent_node.name
            parent_node_style = node_style.copy()
            if node_attr and parent_node.get_attr(node_attr):
                parent_node_style.update(parent_node.get_attr(node_attr))
            pydot_parent = pydot.Node(
                name=parent_name, label=parent_name, **parent_node_style
            )
            _graph.add_node(pydot_parent)

            edge = pydot.Edge(parent_name, child_name, **edge_style)
            _graph.add_edge(edge)

    return _graph
