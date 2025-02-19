import unittest

import pytest

from bigtree.node.node import Node
from bigtree.tree.export import print_tree
from bigtree.tree.modify import copy_nodes, copy_nodes_from_tree_to_tree, shift_nodes
from bigtree.tree.search import find_name, find_path
from bigtree.utils.exceptions import NotFoundError, TreeError
from tests.node.test_basenode import (
    assert_tree_structure_basenode_root_attr,
    assert_tree_structure_basenode_root_generic,
)
from tests.node.test_node import assert_tree_structure_node_root_generic


class TestCopyNodes(unittest.TestCase):
    def setUp(self):
        """
        Tree should have structure
        a
        |-- b
        |   |-- d
        |   +-- e
        |       |-- g
        |       +-- h
        +-- c
            +-- f

        Tree root should have structure
        a
        ├── b
        ├── c
        ├── d
        ├── e
        ├── f
        ├── g
        └── h

        Tree root_other should have structure
        aa
        ├── b
        ├── c
        ├── d
        ├── e
        ├── f
        ├── g
        └── h

        Tree root_overriding should have structure
        a
        ├── aa
        │   └── bb
        │       └── cc
        │           └── dd
        └── bb
            └── cc2
        """
        a = Node(name="a", age=90)
        b = Node(name="b", age=65)
        c = Node(name="c", age=60)
        d = Node(name="d", age=40)
        e = Node(name="e", age=35)
        f = Node(name="f", age=38)
        g = Node(name="g", age=10)
        h = Node(name="h", age=6)

        b.parent = a
        c.parent = a
        d.parent = a
        e.parent = a
        f.parent = a
        g.parent = a
        h.parent = a

        self.root = a

        aa = Node(name="aa", age=90)
        b = Node(name="b", age=65)
        c = Node(name="c", age=60)
        d = Node(name="d", age=40)
        e = Node(name="e", age=35)
        f = Node(name="f", age=38)
        g = Node(name="g", age=10)
        h = Node(name="h", age=6)

        b.parent = aa
        c.parent = aa
        d.parent = aa
        e.parent = aa
        f.parent = aa
        g.parent = aa
        h.parent = aa

        self.root_other = aa

        root_overriding = Node("a")
        new_aa = Node("aa", parent=root_overriding)
        new_bb = Node("bb", parent=new_aa)
        new_cc = Node("cc", age=1, parent=new_bb)
        new_dd = Node("dd", age=2)
        new_dd.parent = new_cc
        bb2 = Node("bb")
        cc2 = Node("cc2")
        bb2.parent = root_overriding
        cc2.parent = bb2
        self.root_overriding = root_overriding

    def tearDown(self):
        self.root = None

    def test_copy_nodes(self):
        from_paths = ["d"]
        to_paths = ["a/b/c/d"]
        copy_nodes(self.root, from_paths, to_paths)
        assert self.root.max_depth == 4, "Shift did not create a tree of depth 4"
        assert find_path(self.root, "a/d"), "Original node is not there"
        assert find_path(self.root, "a/b/c/d"), "Copied node is not there"

    def test_copy_nodes_invalid_type(self):
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, {}, [])
        assert str(exc_info.value).startswith("Invalid type")

    def test_copy_nodes_unequal_length(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Paths are different length")

    def test_copy_nodes_invalid_paths(self):
        from_paths = ["d"]
        to_paths = ["a/b/e"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Unable to assign")

    def test_copy_nodes_invalid_from_paths(self):
        from_paths = ["i"]
        to_paths = ["a/b/i"]
        with pytest.raises(NotFoundError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Unable to find from_path")

    def test_copy_nodes_invalid_to_paths(self):
        from_paths = ["d"]
        to_paths = ["aa/b/d"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith(
            "Invalid path in `to_paths` not starting with the root node"
        )

    def test_copy_nodes_create_intermediate_path(self):
        from_paths = ["d"]
        to_paths = ["a/b/c/d"]
        copy_nodes(self.root, from_paths, to_paths)
        assert self.root.max_depth == 4, "Shift did not create a tree of depth 4"

    def test_copy_nodes_delete_error(self):
        from_paths = ["d"]
        to_paths = [None]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert (
            str(exc_info.value)
            == "Deletion of node will not happen if `copy=True`, check your `copy` parameter."
        )

    def test_copy_nodes_delete_error2(self):
        from_paths = ["d"]
        to_paths = [""]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert (
            str(exc_info.value)
            == "Deletion of node will not happen if `copy=True`, check your `copy` parameter."
        )

    # sep
    def test_copy_nodes_leading_sep(self):
        from_paths = ["/d", "e", "g", "/h", "/f"]
        to_paths = ["/a/b/d", "a/b/e", "/a/b/e/g", "a/b/e/h", "/a/c/f"]
        copy_nodes(self.root, from_paths, to_paths)

        # Delete original nodes
        from_paths = ["/a/d", "/a/e", "/a/g", "/a/h", "/a/f"]
        to_paths = [None, None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_copy_nodes_trailing_sep(self):
        from_paths = ["d", "e/", "g/", "h", "f/"]
        to_paths = ["a/b/d", "a/b/e/", "a/b/e/g/", "a/b/e/h/", "a/c/f"]
        copy_nodes(self.root, from_paths, to_paths)

        # Delete original nodes
        from_paths = ["/a/d", "/a/e", "/a/g", "/a/h", "/a/f"]
        to_paths = [None, None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_copy_nodes_sep_undefined(self):
        from_paths = ["\\d", "\\e", "\\g", "\\h", "\\f"]
        to_paths = ["a\\b\\d", "a\\b\\e", "a\\b\\e\\g", "a\\b\\e\\h", "a\\c\\f"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Unable to assign from_path")

    def test_copy_nodes_sep(self):
        from_paths = ["\\d", "\\e", "\\g", "\\h", "\\f"]
        to_paths = ["a\\b\\d", "a\\b\\e", "a\\b\\e\\g", "a\\b\\e\\h", "a\\c\\f"]
        copy_nodes(self.root, from_paths, to_paths, sep="\\")

        # Delete original nodes
        from_paths = ["\\a\\d", "\\a\\e", "\\a\\g", "\\a\\h", "\\a\\f"]
        to_paths = [None, None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths, sep="\\")

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_copy_nodes_sep_different(self):
        # Delete intermediate nodes
        from_paths = ["\\a\\b", "\\a\\c", "\\a\\e"]
        to_paths = [None, None, None]
        shift_nodes(self.root, from_paths, to_paths, sep="\\")

        # Create intermediate nodes
        from_paths = ["\\d", "\\g", "\\h", "\\f"]
        to_paths = ["a\\b\\d", "a\\b\\e\\g", "a\\b\\e\\h", "a\\c\\f"]
        copy_nodes(self.root, from_paths, to_paths, sep="\\")

        # Delete original nodes
        from_paths = ["\\a\\d", "\\a\\g", "\\a\\h", "\\a\\f"]
        to_paths = [None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths, sep="\\")

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # skippable
    def test_copy_nodes_skippable(self):
        from_paths = ["i", "d", "e", "g", "h", "f"]
        to_paths = ["a/c/f/i", "a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        with pytest.raises(NotFoundError):
            copy_nodes(self.root, from_paths, to_paths)

        copy_nodes(self.root, from_paths, to_paths, skippable=True)

        # Delete original nodes
        from_paths = ["a/d", "a/e", "a/g", "a/h", "a/f"]
        to_paths = [None, None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # overriding
    def test_copy_nodes_delete_and_overriding_error(self):
        new_aa = Node("aa", parent=self.root)
        new_d = Node("d")
        new_d.parent = new_aa
        from_paths = ["/a/d", "aa/d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        with pytest.raises(TreeError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith(
            "Path a/b/d already exists and unable to override"
        )

    def test_copy_nodes_delete_and_overriding(self):
        new_aa = Node("aa", parent=self.root)
        new_d = Node("d", age=1)
        new_d.parent = new_aa
        from_paths = ["/a/d", "aa/d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        copy_nodes(self.root, from_paths, to_paths, overriding=True)

        # Delete original nodes
        from_paths = ["a/aa", "a/d", "a/e", "a/g", "a/h", "a/f"]
        to_paths = [None, None, None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root, d=("d", 1))
        assert_tree_structure_node_root_generic(self.root)

    def test_copy_nodes_overriding(self):
        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        copy_nodes(
            self.root_overriding,
            from_paths,
            to_paths,
            overriding=True,
        )
        assert (
            len(list(self.root_overriding.children)) == 2
        ), f"Node children not merged, {print_tree(self.root_overriding)}"
        assert find_path(
            self.root_overriding, "/a/bb/cc"
        ), "Node children not merged, new children not present"
        assert not find_path(
            self.root_overriding, "/a/bb/cc2"
        ), "Node children not merged, original children not overridden"
        assert (
            find_path(self.root_overriding, "/a/bb/cc").get_attr("age") == 1
        ), f"Merged children not overridden, {print_tree(self.root_overriding)}"
        assert len(
            list(find_path(self.root_overriding, "/a/aa").children)
        ), "Children of node parent deleted (not copied)"

    # merge_children
    def test_copy_nodes_merge_children(self):
        from_paths = ["aa/bb/cc"]
        to_paths = ["/a/cc"]
        copy_nodes(self.root_overriding, from_paths, to_paths, merge_children=True)
        assert len(list(self.root_overriding.children)) == 3
        assert find_path(self.root_overriding, "a/dd"), "Node children not merged"
        assert (
            find_path(self.root_overriding, "a/dd").get_attr("age") == 2
        ), f"Merged children not overridden, {print_tree(self.root_overriding)}"
        assert len(
            list(find_path(self.root_overriding, "a/aa/bb").children)
        ), "Children of node parent deleted (not copied)"

    def test_copy_nodes_merge_children_non_overriding(self):
        from_paths = ["aa/bb"]
        to_paths = ["/a/bb"]
        copy_nodes(self.root_overriding, from_paths, to_paths, merge_children=True)
        assert len(list(self.root_overriding.children)) == 2
        assert find_path(
            self.root_overriding, "/a/bb/cc/dd"
        ), "Node children not merged"
        assert (
            find_path(self.root_overriding, "/a/bb/cc/dd").get_attr("age") == 2
        ), f"Merged children not overridden, {print_tree(self.root_overriding)}"
        assert len(
            list(find_path(self.root_overriding, "/a/aa").children)
        ), "Children of node parent deleted (not copied)"

    def test_copy_nodes_merge_children_non_overriding_error(self):
        bb = find_path(self.root_overriding, "/a/bb")
        cc = Node("cc")
        cc.parent = bb

        from_paths = ["aa/bb"]
        to_paths = ["/a/bb"]
        with pytest.raises(TreeError) as exc_info:
            copy_nodes(self.root_overriding, from_paths, to_paths, merge_children=True)
        assert str(exc_info.value).startswith("Error: Duplicate node with same path")

    def test_copy_nodes_same_node_error(self):
        from_paths = ["d"]
        to_paths = ["a/d"]
        with pytest.raises(TreeError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Attempting to shift the same node")

    def test_copy_nodes_same_node_merge_children(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["b"]
        to_paths = ["a/b"]
        copy_nodes(self.root, from_paths, to_paths, merge_children=True)
        assert len(list(self.root.children)) == 3, "Node b is not removed"
        assert not find_path(self.root, "a/b"), "Node b is not removed"
        assert find_path(self.root, "a/c"), "Node c is gone"
        assert find_path(self.root, "a/d"), "Node d parent is not Node a"
        assert find_path(self.root, "a/e"), "Node e parent is not Node a"

    # merge_leaves
    def test_copy_nodes_merge_leaves(self):
        from_paths = ["a/aa/bb"]
        to_paths = ["/a/cc/bb"]
        copy_nodes(self.root_overriding, from_paths, to_paths, merge_leaves=True)

        assert find_path(
            self.root_overriding, "a/aa/bb/cc"
        ), "a/aa/bb/cc path got removed"
        assert find_path(
            self.root_overriding, "a/aa/bb/cc/dd"
        ), "dd did not copy (old location not present)"
        assert find_path(
            self.root_overriding, "a/cc/dd"
        ), "dd did not shift (new location not present)"

    def test_copy_nodes_merge_leaves_non_overriding(self):
        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        copy_nodes(self.root_overriding, from_paths, to_paths, merge_leaves=True)

        assert find_path(
            self.root_overriding, "a/aa/bb/cc"
        ), "a/aa/bb/cc path got removed"
        assert find_path(
            self.root_overriding, "a/aa/bb/cc/dd"
        ), "dd did not copy (old location not present)"
        assert find_path(
            self.root_overriding, "a/bb/dd"
        ), "dd did not shift (new location not present)"
        assert find_path(self.root_overriding, "a/bb/cc2"), "cc2 got replaced"

    def test_copy_nodes_merge_leaves_non_overriding_error(self):
        bb = find_path(self.root_overriding, "/a/bb")
        dd = Node("dd")
        dd.parent = bb

        from_paths = ["a/aa"]
        to_paths = ["/a/bb/aa"]
        with pytest.raises(TreeError) as exc_info:
            copy_nodes(self.root_overriding, from_paths, to_paths, merge_leaves=True)
        assert str(exc_info.value).startswith("Error: Duplicate node with same path")

    def test_copy_nodes_same_node_merge_leaves(self):
        a = Node("a", age=90)
        self.root_other.parent = a

        from_paths = ["a/aa/d", "a/aa/e", "a/aa/g", "a/aa/h", "a/aa/f"]
        to_paths = ["a/aa/b/d", "a/aa/b/e", "a/aa/b/e/g", "a/aa/b/e/h", "a/aa/c/f"]
        shift_nodes(a, from_paths, to_paths)

        from_paths = ["a/aa"]
        to_paths = ["a/aa"]
        copy_nodes(a, from_paths, to_paths, merge_leaves=True)

        assert [child.name for child in a.children] == [
            "aa",
            "d",
            "g",
            "h",
            "f",
        ], f"Tree has children {a.children}, expected ['aa', 'd', 'g', 'h', 'f']"
        assert find_path(a, "a/aa/b/d"), "a/aa/b/d path got removed"
        assert find_path(a, "a/aa/b/e/g"), "a/aa/b/e/g path got removed"
        assert find_path(a, "a/aa/b/e/h"), "a/aa/b/e/h path got removed"
        assert find_path(a, "a/aa/c/f"), "a/aa/c/f path got removed"

    # delete_children
    def test_copy_nodes_delete_children(self):
        g = find_name(self.root, "g")
        h = find_name(self.root, "h")
        g.children = [Node("i"), Node("j")]
        h.children = [Node("i"), Node("j")]
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        copy_nodes(self.root, from_paths, to_paths, delete_children=True)

        # Delete original nodes
        from_paths = ["a/d", "a/e", "a/g", "a/h", "a/f"]
        to_paths = [None, None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # merge_children, overriding
    def test_copy_nodes_merge_children_overriding(self):
        new_aa = Node("aa", parent=self.root)
        new_bb = Node("bb", parent=new_aa)
        new_cc = Node("cc", age=1)
        new_cc.parent = new_bb
        bb2 = Node("bb")
        cc2 = Node("cc2")
        bb2.parent = self.root
        cc2.parent = bb2

        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        copy_nodes(
            self.root, from_paths, to_paths, overriding=True, merge_children=True
        )
        assert (
            len(list(self.root.children)) == 4
        ), f"Node children not merged, {print_tree(self.root)}"
        assert find_path(
            self.root, "/a/bb/cc"
        ), "Node children not merged, new children not present"
        assert not find_path(
            self.root, "/a/bb/cc2"
        ), "Node children not merged, original children not overridden"
        assert (
            find_path(self.root, "/a/bb/cc").get_attr("age") == 1
        ), f"Merged children not overridden, {print_tree(self.root)}"
        assert len(list(find_path(self.root, "/a/aa").children)), "Node parent deleted"

    # merge_leaves, overriding
    def test_copy_nodes_merge_leaves_overriding(self):
        new_aa = Node("aa", parent=self.root)
        new_bb = Node("bb", parent=new_aa)
        new_cc = Node("cc", age=1)
        new_cc.parent = new_bb
        bb2 = Node("bb")
        cc2 = Node("cc2")
        bb2.parent = self.root
        cc2.parent = bb2

        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        copy_nodes(self.root, from_paths, to_paths, overriding=True, merge_leaves=True)
        assert (
            len(list(self.root.children)) == 4
        ), f"Node children not merged, {print_tree(self.root)}"
        assert find_path(
            self.root, "/a/bb/cc"
        ), "Node children not merged, new children not present"
        assert not find_path(
            self.root, "/a/bb/cc2"
        ), "Node children not merged, original children not overridden"
        assert (
            find_path(self.root, "/a/bb/cc").get_attr("age") == 1
        ), f"Merged children not overridden, {print_tree(self.root)}"
        assert len(list(find_path(self.root, "/a/aa").children)), "Node parent deleted"

    # merge_children, merge_leaves
    def test_copy_nodes_merge_children_and_leaf_error(self):
        a = Node("a", age=90)
        self.root_other.parent = a

        from_paths = ["a/aa/d", "a/aa/e", "a/aa/g", "a/aa/h", "a/aa/f"]
        to_paths = ["a/aa/b/d", "a/aa/b/e", "a/aa/b/e/g", "a/aa/b/e/h", "a/aa/c/f"]
        shift_nodes(a, from_paths, to_paths)

        from_paths = ["a/aa"]
        to_paths = ["a/bb/aa"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(a, from_paths, to_paths, merge_children=True, merge_leaves=True)
        assert str(exc_info.value).startswith(
            "Invalid shifting, can only specify one type of merging"
        )

    # merge_children, delete_children
    def test_copy_nodes_merge_children_and_delete_children(self):
        from_paths = ["d", "e", "g", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        h2 = Node("h", age=6)
        h2.children = [Node("i"), Node("j")]
        h = find_name(self.root, "h")
        h2.parent = h
        from_paths = ["a/h"]
        to_paths = ["a/b/e/h"]
        copy_nodes(
            self.root, from_paths, to_paths, merge_children=True, delete_children=True
        )

        # Delete original nodes
        from_paths = ["a/h"]
        to_paths = [None]
        shift_nodes(self.root, from_paths, to_paths)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # merge_leaves, delete_children
    def test_copy_nodes_merge_leaves_and_delete_children(self):
        from_paths = ["d", "e", "g", "f", "h"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/c/f", "a/i/j/k/h"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/i"]
        to_paths = ["a/b/e/i"]
        copy_nodes(
            self.root, from_paths, to_paths, merge_leaves=True, delete_children=True
        )
        i = find_path(self.root, "a/i")
        i.parent = None
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # with_full_path
    def test_copy_nodes_with_full_path(self):
        from_paths = ["a/d", "a/e", "a/g", "a/h", "a/f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        copy_nodes(self.root, from_paths, to_paths, with_full_path=True)

        # Delete original nodes
        from_paths = ["a/d", "a/e", "a/g", "a/h", "a/f"]
        to_paths = [None, None, None, None, None]
        shift_nodes(self.root, from_paths, to_paths, with_full_path=True)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_copy_nodes_with_full_path_error(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes(self.root, from_paths, to_paths, with_full_path=True)
        assert str(exc_info.value).startswith(
            "Invalid path in `from_paths` not starting with the root node"
        )


class TestShiftNodes(unittest.TestCase):
    def setUp(self):
        """
        Tree should have structure
        a
        |-- b
        |   |-- d
        |   +-- e
        |       |-- g
        |       +-- h
        +-- c
            +-- f

        Tree root should have structure
        a
        ├── b
        ├── c
        ├── d
        ├── e
        ├── f
        ├── g
        └── h

        Tree root_other should have structure
        aa
        ├── b
        ├── c
        ├── d
        ├── e
        ├── f
        ├── g
        └── h

        Tree root_overriding should have structure
        a
        ├── aa
        │   └── bb
        │       └── cc
        │           └── dd
        └── bb
            └── cc2
        """
        a = Node(name="a", age=90)
        b = Node(name="b", age=65)
        c = Node(name="c", age=60)
        d = Node(name="d", age=40)
        e = Node(name="e", age=35)
        f = Node(name="f", age=38)
        g = Node(name="g", age=10)
        h = Node(name="h", age=6)

        b.parent = a
        c.parent = a
        d.parent = a
        e.parent = a
        f.parent = a
        g.parent = a
        h.parent = a

        self.root = a

        aa = Node(name="aa", age=90)
        b = Node(name="b", age=65)
        c = Node(name="c", age=60)
        d = Node(name="d", age=40)
        e = Node(name="e", age=35)
        f = Node(name="f", age=38)
        g = Node(name="g", age=10)
        h = Node(name="h", age=6)

        b.parent = aa
        c.parent = aa
        d.parent = aa
        e.parent = aa
        f.parent = aa
        g.parent = aa
        h.parent = aa

        self.root_other = aa

        root_overriding = Node("a")
        new_aa = Node("aa", parent=root_overriding)
        new_bb = Node("bb", parent=new_aa)
        new_cc = Node("cc", age=1, parent=new_bb)
        new_dd = Node("dd", age=2)
        new_dd.parent = new_cc
        bb2 = Node("bb")
        cc2 = Node("cc2")
        bb2.parent = root_overriding
        cc2.parent = bb2
        self.root_overriding = root_overriding

    def tearDown(self):
        self.root = None

    def test_shift_nodes(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_shift_nodes_invalid_type(self):
        with pytest.raises(ValueError) as exc_info:
            shift_nodes(self.root, {}, [])
        assert str(exc_info.value).startswith("Invalid type")

    def test_shift_nodes_unequal_length(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d"]
        with pytest.raises(ValueError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Paths are different length")

    def test_shift_nodes_invalid_paths(self):
        from_paths = ["d"]
        to_paths = ["a/b/e"]
        with pytest.raises(ValueError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Unable to assign")

    def test_shift_nodes_invalid_from_paths(self):
        from_paths = ["i"]
        to_paths = ["a/b/i"]
        with pytest.raises(NotFoundError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Unable to find from_path")

    def test_shift_nodes_invalid_to_paths(self):
        from_paths = ["d"]
        to_paths = ["aa/b/d"]
        with pytest.raises(ValueError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith(
            "Invalid path in `to_paths` not starting with the root node"
        )

    def test_shift_nodes_create_intermediate_path(self):
        from_paths = ["d"]
        to_paths = ["a/b/c/d"]
        shift_nodes(self.root, from_paths, to_paths)
        assert self.root.max_depth == 4, "Shift did not create a tree of depth 4"

    # sep
    def test_shift_nodes_leading_sep(self):
        from_paths = ["/d", "e", "g", "/h", "/f"]
        to_paths = ["/a/b/d", "a/b/e", "/a/b/e/g", "a/b/e/h", "/a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_shift_nodes_trailing_sep(self):
        from_paths = ["d/", "e", "g/", "h", "f/"]
        to_paths = ["a/b/d/", "a/b/e", "a/b/e/g", "a/b/e/h/", "a/c/f/"]
        shift_nodes(self.root, from_paths, to_paths)
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_shift_nodes_sep_undefined(self):
        from_paths = ["\\d", "\\e", "\\g", "\\h", "\\f"]
        to_paths = ["a\\b\\d", "a\\b\\e", "a\\b\\e\\g", "a\\b\\e\\h", "a\\c\\f"]
        with pytest.raises(ValueError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Unable to assign from_path")

    def test_shift_nodes_sep(self):
        from_paths = ["\\d", "\\e", "\\g", "\\h", "\\f"]
        to_paths = ["a\\b\\d", "a\\b\\e", "a\\b\\e\\g", "a\\b\\e\\h", "a\\c\\f"]
        shift_nodes(self.root, from_paths, to_paths, sep="\\")
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # skippable
    def test_shift_nodes_skippable(self):
        from_paths = ["i", "d", "e", "g", "h", "f"]
        to_paths = ["a/c/f/i", "a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        with pytest.raises(NotFoundError):
            shift_nodes(self.root, from_paths, to_paths)

        shift_nodes(self.root, from_paths, to_paths, skippable=True)
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # overriding
    def test_shift_nodes_delete_and_overriding_error(self):
        new_aa = Node("aa", parent=self.root)
        new_d = Node("d")
        new_d.parent = new_aa
        from_paths = ["/a/d", "aa/d", "e", "g", "h", "f", "a/aa"]
        to_paths = ["a/b/d", "a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f", None]
        with pytest.raises(TreeError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith(
            "Path a/b/d already exists and unable to override"
        )

    def test_shift_nodes_delete_and_overriding(self):
        new_aa = Node("aa", parent=self.root)
        new_d = Node("d", age=1)
        new_d.parent = new_aa
        from_paths = ["/a/d", "aa/d", "e", "g", "h", "f", "a/aa"]
        to_paths = ["a/b/d", "a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f", None]
        shift_nodes(self.root, from_paths, to_paths, overriding=True)
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root, d=("d", 1))
        assert_tree_structure_node_root_generic(self.root)

    def test_shift_nodes_overriding(self):
        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        shift_nodes(
            self.root_overriding,
            from_paths,
            to_paths,
            overriding=True,
        )
        assert (
            len(list(self.root_overriding.children)) == 2
        ), f"Node children not merged, {print_tree(self.root_overriding)}"
        assert find_path(
            self.root_overriding, "a/bb/cc"
        ), "Node children not merged, new children not present"
        assert not find_path(
            self.root_overriding, "a/bb/cc2"
        ), "Node children not merged, original children not overridden"
        assert (
            find_path(self.root_overriding, "a/bb/cc").get_attr("age") == 1
        ), f"Merged children not overridden, {print_tree(self.root_overriding)}"
        assert not len(
            list(find_path(self.root_overriding, "a/aa").children)
        ), "Children of node parent not deleted"

    # merge_children
    def test_shift_nodes_merge_children(self):
        from_paths = ["aa/bb/cc"]
        to_paths = ["/a/cc"]
        shift_nodes(self.root_overriding, from_paths, to_paths, merge_children=True)
        assert len(list(self.root_overriding.children)) == 3
        assert find_path(self.root_overriding, "a/dd"), "Node children not merged"
        assert (
            find_path(self.root_overriding, "a/dd").get_attr("age") == 2
        ), f"Merged children not overridden, {print_tree(self.root_overriding)}"
        assert not len(
            list(find_path(self.root_overriding, "a/aa/bb").children)
        ), "Children of node parent not deleted"

    def test_shift_nodes_merge_children_non_overriding(self):
        from_paths = ["aa/bb"]
        to_paths = ["/a/bb"]
        shift_nodes(self.root_overriding, from_paths, to_paths, merge_children=True)
        assert len(list(self.root_overriding.children)) == 2
        assert find_path(self.root_overriding, "a/bb/cc/dd"), "Node children not merged"
        assert (
            find_path(self.root_overriding, "a/bb/cc/dd").get_attr("age") == 2
        ), f"Merged children not overridden, {print_tree(self.root_overriding)}"
        assert not len(
            list(find_path(self.root_overriding, "a/aa").children)
        ), "Children of node parent not deleted"

    def test_shift_nodes_merge_children_non_overriding_error(self):
        bb = find_path(self.root_overriding, "/a/bb")
        cc = Node("cc")
        cc.parent = bb

        from_paths = ["aa/bb"]
        to_paths = ["/a/bb"]
        with pytest.raises(TreeError) as exc_info:
            shift_nodes(self.root_overriding, from_paths, to_paths, merge_children=True)
        assert str(exc_info.value).startswith("Error: Duplicate node with same path")

    def test_shift_nodes_same_node_error(self):
        from_paths = ["d"]
        to_paths = ["a/d"]
        with pytest.raises(TreeError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths)
        assert str(exc_info.value).startswith("Attempting to shift the same node")

    def test_shift_nodes_same_node_merge_children(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["b"]
        to_paths = ["a/b"]
        shift_nodes(self.root, from_paths, to_paths, merge_children=True)
        assert len(list(self.root.children)) == 3, "Node b is not removed"
        assert not find_path(self.root, "a/b"), "Node b is not removed"
        assert find_path(self.root, "a/c"), "Node c is gone"
        assert find_path(self.root, "a/d"), "Node d parent is not Node a"
        assert find_path(self.root, "a/e"), "Node e parent is not Node a"

    # merge_leaves
    def test_shift_nodes_merge_leaves(self):
        from_paths = ["a/aa/bb"]
        to_paths = ["/a/cc/bb"]
        shift_nodes(self.root_overriding, from_paths, to_paths, merge_leaves=True)

        assert find_path(
            self.root_overriding, "a/aa/bb/cc"
        ), "a/aa/bb/cc path got removed"
        assert not find_path(
            self.root_overriding, "a/aa/bb/cc/dd"
        ), "dd did not shift (old location still present)"
        assert find_path(
            self.root_overriding, "a/cc/dd"
        ), "dd did not shift (new location not present)"

    def test_shift_nodes_merge_leaves_non_overriding(self):
        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        shift_nodes(self.root_overriding, from_paths, to_paths, merge_leaves=True)

        assert find_path(
            self.root_overriding, "a/aa/bb/cc"
        ), "a/aa/bb/cc path got removed"
        assert not find_path(
            self.root_overriding, "a/aa/bb/cc/dd"
        ), "dd did not shift (old location still present)"
        assert find_path(
            self.root_overriding, "a/bb/dd"
        ), "dd did not shift (new location not present)"
        assert find_path(self.root_overriding, "a/bb/cc2"), "cc2 got replaced"

    def test_shift_nodes_merge_leaves_non_overriding_error(self):
        bb = find_path(self.root_overriding, "/a/bb")
        dd = Node("dd")
        dd.parent = bb

        from_paths = ["a/aa"]
        to_paths = ["/a/bb/aa"]
        with pytest.raises(TreeError) as exc_info:
            shift_nodes(self.root_overriding, from_paths, to_paths, merge_leaves=True)
        assert str(exc_info.value).startswith("Error: Duplicate node with same path")

    def test_shift_nodes_same_node_merge_leaves(self):
        a = Node("a", age=90)
        self.root_other.parent = a

        from_paths = ["a/aa/d", "a/aa/e", "a/aa/g", "a/aa/h", "a/aa/f"]
        to_paths = ["a/aa/b/d", "a/aa/b/e", "a/aa/b/e/g", "a/aa/b/e/h", "a/aa/c/f"]
        shift_nodes(a, from_paths, to_paths)

        from_paths = ["a/aa"]
        to_paths = ["a/aa"]
        shift_nodes(a, from_paths, to_paths, merge_leaves=True)
        assert [child.name for child in a.children] == [
            "aa",
            "d",
            "g",
            "h",
            "f",
        ], f"Tree has children {a.children}, expected ['aa', 'd', 'g', 'h', 'f']"
        assert find_path(a, "a/aa/b/e"), "a/aa/b/e path got removed"
        assert find_path(a, "a/aa/c"), "a/aa/c path got removed"
        assert not len(
            find_path(a, "a/aa/b/e").children
        ), "Leaf nodes of a/aa/b/e did not get shifted"
        assert not len(
            find_path(a, "a/aa/c").children
        ), "Leaf nodes of a/aa/c did not get shifted"

    # delete_children
    def test_shift_nodes_delete_children(self):
        g = find_name(self.root, "g")
        h = find_name(self.root, "h")
        g.children = [Node("i"), Node("j")]
        h.children = [Node("i"), Node("j")]
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths, delete_children=True)
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # merge_children, overriding
    def test_shift_nodes_merge_children_overriding(self):
        new_aa = Node("aa", parent=self.root)
        new_bb = Node("bb", parent=new_aa)
        new_cc = Node("cc", age=1)
        new_cc.parent = new_bb
        bb2 = Node("bb")
        cc2 = Node("cc2")
        bb2.parent = self.root
        cc2.parent = bb2

        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        shift_nodes(
            self.root, from_paths, to_paths, overriding=True, merge_children=True
        )
        assert (
            len(list(self.root.children)) == 4
        ), f"Node children not merged, {print_tree(self.root)}"
        assert find_path(
            self.root, "a/bb/cc"
        ), "Node children not merged, new children not present"
        assert not find_path(
            self.root, "a/bb/cc2"
        ), "Node children not merged, original children not overridden"
        assert (
            find_path(self.root, "a/bb/cc").get_attr("age") == 1
        ), f"Merged children not overridden, {print_tree(self.root)}"
        assert not len(
            list(find_path(self.root, "a/aa").children)
        ), "Node parent not deleted"

    # merge_leaves, overriding
    def test_shift_nodes_merge_leaves_overriding(self):
        new_aa = Node("aa", parent=self.root)
        new_bb = Node("bb", parent=new_aa)
        new_cc = Node("cc", age=1)
        new_cc.parent = new_bb
        bb2 = Node("bb")
        cc2 = Node("cc2")
        bb2.parent = self.root
        cc2.parent = bb2

        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/aa/bb"]
        to_paths = ["/a/bb"]
        shift_nodes(self.root, from_paths, to_paths, overriding=True, merge_leaves=True)
        assert (
            len(list(self.root.children)) == 4
        ), f"Node children not merged, {print_tree(self.root)}"
        assert find_path(
            self.root, "a/bb/cc"
        ), "Node children not merged, new children not present"
        assert not find_path(
            self.root, "a/bb/cc2"
        ), "Node children not merged, original children not overridden"
        assert (
            find_path(self.root, "a/bb/cc").get_attr("age") == 1
        ), f"Merged children not overridden, {print_tree(self.root)}"
        assert len(list(find_path(self.root, "a/aa").children)), "Node parent deleted"

    # merge_children, merge_leaves
    def test_shift_nodes_merge_children_and_leaf_error(self):
        a = Node("a", age=90)
        self.root_other.parent = a

        from_paths = ["a/aa/d", "a/aa/e", "a/aa/g", "a/aa/h", "a/aa/f"]
        to_paths = ["a/aa/b/d", "a/aa/b/e", "a/aa/b/e/g", "a/aa/b/e/h", "a/aa/c/f"]
        shift_nodes(a, from_paths, to_paths)

        from_paths = ["a/aa"]
        to_paths = ["a/bb/aa"]
        with pytest.raises(ValueError) as exc_info:
            shift_nodes(a, from_paths, to_paths, merge_children=True, merge_leaves=True)
        assert str(exc_info.value).startswith(
            "Invalid shifting, can only specify one type of merging"
        )

    # merge_children, delete_children
    def test_shift_nodes_merge_children_and_delete_children(self):
        from_paths = ["d", "e", "g", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        h2 = Node("h", age=6)
        h2.children = [Node("i"), Node("j")]
        h = find_name(self.root, "h")
        h2.parent = h
        from_paths = ["a/h"]
        to_paths = ["a/b/e/h"]
        shift_nodes(
            self.root, from_paths, to_paths, merge_children=True, delete_children=True
        )
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # merge_leaves, delete_children
    def test_shift_nodes_merge_leaves_and_delete_children(self):
        from_paths = ["d", "e", "g", "f", "h"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/c/f", "a/i/j/k/h"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/i"]
        to_paths = ["a/b/e/i"]
        shift_nodes(
            self.root, from_paths, to_paths, merge_leaves=True, delete_children=True
        )
        i = find_path(self.root, "a/i")
        i.parent = None
        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    # with_full_path
    def test_shift_nodes_with_full_path(self):
        from_paths = ["a/d", "a/e", "a/g", "a/h", "a/f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths, with_full_path=True)

        assert_tree_structure_basenode_root_generic(self.root)
        assert_tree_structure_basenode_root_attr(self.root)
        assert_tree_structure_node_root_generic(self.root)

    def test_shift_nodes_with_full_path_error(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        with pytest.raises(ValueError) as exc_info:
            shift_nodes(self.root, from_paths, to_paths, with_full_path=True)
        assert str(exc_info.value).startswith(
            "Invalid path in `from_paths` not starting with the root node"
        )


class TestCopyNodesTwoTrees(unittest.TestCase):
    def setUp(self):
        """
        Tree should have structure
        a
        |-- b
        |   |-- d
        |   +-- e
        |       |-- g
        |       +-- h
        +-- c
            +-- f

        Tree root should have structure
        a [age=90]
        ├── b [age=65]
        ├── c [age=60]
        ├── d [age=40]
        ├── e [age=35]
        ├── f [age=38]
        ├── g [age=10]
        └── h [age=6]

        Tree root_other should have structure
        a [age=90]

        Tree root_other_full should have structure
        a [age=90]
        ├── b [age=65]
        │   └── d [age=40]
        └── c [age=60]
            └── f [age=38]

        Tree root_other_full_wrong should have structure
        a [age=90]
        ├── b [age=65]
        └── c [age=1]
            └── f
        """
        a = Node(name="a", age=90)
        b = Node(name="b", age=65)
        c = Node(name="c", age=60)
        d = Node(name="d", age=40)
        e = Node(name="e", age=35)
        f = Node(name="f", age=38)
        g = Node(name="g", age=10)
        h = Node(name="h", age=6)

        b.parent = a
        c.parent = a
        d.parent = a
        e.parent = a
        f.parent = a
        g.parent = a
        h.parent = a

        self.root = a

        root_other = Node("a", age=90)
        self.root_other = root_other

        root_other_full = Node("a", age=90)
        b = Node("b", age=65, parent=root_other_full)
        d = Node("d", age=40)
        d.parent = b
        c = Node("c", age=60, parent=root_other_full)
        f = Node("f", age=38)
        f.parent = c
        self.root_other_full = root_other_full

        root_other_full_wrong = Node("a", age=90)
        b = Node("b", age=65)
        b.parent = root_other_full_wrong
        c = Node("c", age=1, parent=root_other_full_wrong)
        f = Node("f")
        f.parent = c
        self.root_other_full_wrong = root_other_full_wrong

    def tearDown(self):
        self.root = None

    def test_copy_nodes_from_tree_to_tree(self):
        from_paths = ["b", "c", "d", "e", "f", "g", "h"]
        to_paths = ["a/b", "a/c", "a/b/d", "a/b/e", "a/c/f", "a/b/e/g", "a/b/e/h"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
        )
        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other)
        assert_tree_structure_node_root_generic(self.root_other)
        assert self.root.max_depth == 2, "Copying changes original tree"

    def test_copy_nodes_from_tree_to_tree_reversed_error(self):
        from_paths = ["b", "c", "d", "e", "f", "g", "h"][::-1]
        to_paths = ["a/b", "a/c", "a/b/d", "a/b/e", "a/c/f", "a/b/e/g", "a/b/e/h"][::-1]
        with pytest.raises(TreeError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert "already exists and unable to override" in str(exc_info.value)

    def test_copy_nodes_from_tree_to_tree_invalid_type(self):
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths={},
                to_paths=[],
            )
        assert str(exc_info.value).startswith("Invalid type")

    def test_copy_nodes_from_tree_to_tree_unequal_length(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert str(exc_info.value).startswith("Paths are different length")

    def test_copy_nodes_from_tree_to_tree_invalid_paths(self):
        from_paths = ["d"]
        to_paths = ["a/b/e"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert str(exc_info.value).startswith("Unable to assign")

    def test_copy_nodes_from_tree_to_tree_invalid_from_paths(self):
        from_paths = ["i"]
        to_paths = ["a/b/i"]
        with pytest.raises(NotFoundError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert str(exc_info.value).startswith("Unable to find from_path")

    def test_copy_nodes_from_tree_to_tree_invalid_to_paths(self):
        from_paths = ["d"]
        to_paths = ["aa/b/d"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert str(exc_info.value).startswith(
            "Invalid path in `to_paths` not starting with the root node"
        )

    def test_copy_nodes_create_intermediate_path(self):
        from_paths = ["d"]
        to_paths = ["a/b/c/d"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
        )
        assert self.root_other.max_depth == 4, "Shift did not create a tree of depth 4"

    def test_copy_nodes_from_tree_to_tree_delete_error(self):
        from_paths = ["d"]
        to_paths = [None]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert (
            str(exc_info.value)
            == "Deletion of node will not happen if `copy=True`, check your `copy` parameter."
        )

    def test_copy_nodes_from_tree_to_tree_delete_error2(self):
        from_paths = ["d"]
        to_paths = [""]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert (
            str(exc_info.value)
            == "Deletion of node will not happen if `copy=True`, check your `copy` parameter."
        )

    # sep
    def test_copy_nodes_from_tree_to_tree_leading_sep(self):
        from_paths = ["/b", "c", "/d", "e", "g", "h", "f"]
        to_paths = [
            "/a/b",
            "a/c",
            "a/b/d",
            "/a/b/e",
            "a/b/e/g",
            "a/b/e/h",
            "a/c/f",
        ]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
        )

        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other)
        assert_tree_structure_node_root_generic(self.root_other)

    def test_copy_nodes_from_tree_to_tree_different_sep(self):
        from_paths = ["b/", "c", "d/", "e", "g", "h", "f"]
        to_paths = [
            "a/b/",
            "a/c",
            "a/b/d",
            "a/b/e/",
            "a/b/e/g",
            "a/b/e/h",
            "a/c/f",
        ]
        self.root_other.sep = "\\"
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
        )
        self.root_other.sep = "/"

        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other)
        assert_tree_structure_node_root_generic(self.root_other)

    def test_copy_nodes_from_tree_to_tree_trailing_sep(self):
        from_paths = ["b/", "c", "d/", "e", "g", "h", "f"]
        to_paths = [
            "a/b/",
            "a/c",
            "a/b/d",
            "a/b/e/",
            "a/b/e/g",
            "a/b/e/h",
            "a/c/f",
        ]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
        )

        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other)
        assert_tree_structure_node_root_generic(self.root_other)

    def test_copy_nodes_from_tree_to_tree_sep_undefined(self):
        from_paths = ["\\d", "\\e", "\\g", "\\h", "\\f"]
        to_paths = ["a\\b\\d", "a\\b\\e", "a\\b\\e\\g", "a\\b\\e\\h", "a\\c\\f"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert str(exc_info.value).startswith("Unable to assign from_path")

    def test_copy_nodes_from_tree_to_tree_sep(self):
        from_paths = ["\\b", "\\c", "\\d", "\\e", "\\g", "\\h", "\\f"]
        to_paths = [
            "a\\b",
            "a\\c",
            "a\\b\\d",
            "a\\b\\e",
            "a\\b\\e\\g",
            "a\\b\\e\\h",
            "a\\c\\f",
        ]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
            sep="\\",
        )

        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other)
        assert_tree_structure_node_root_generic(self.root_other)

    # skippable
    def test_copy_nodes_skippable(self):
        from_paths = ["i", "b", "c", "d", "e", "g", "h", "f"]
        to_paths = [
            "a/c/f/i",
            "a/b",
            "a/c",
            "a/b/d",
            "a/b/e",
            "a/b/e/g",
            "a/b/e/h",
            "a/c/f",
        ]
        with pytest.raises(NotFoundError):
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )

        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
            skippable=True,
        )

        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other)
        assert_tree_structure_node_root_generic(self.root_other)

    # overriding
    def test_copy_nodes_from_tree_to_tree_delete_and_overriding_error(self):
        new_aa = Node("aa", parent=self.root)
        new_d = Node("d")
        new_d.parent = new_aa
        from_paths = ["/a/d", "aa/d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        with pytest.raises(TreeError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
            )
        assert str(exc_info.value).startswith(
            "Path a/b/d already exists and unable to override"
        )

    def test_copy_nodes_from_tree_to_tree_delete_and_overriding(self):
        new_aa = Node("aa", parent=self.root)
        new_d = Node("d", age=1)
        new_d.parent = new_aa
        from_paths = ["a/b", "a/c", "/a/d", "aa/d", "e", "g", "h", "f"]
        to_paths = [
            "a/b",
            "a/c",
            "a/b/d",
            "a/b/d",
            "a/b/e",
            "a/b/e/g",
            "a/b/e/h",
            "a/c/f",
        ]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
            overriding=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other, d=("d", 1))
        assert_tree_structure_node_root_generic(self.root_other)

    def test_copy_nodes_from_tree_to_tree_overriding(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/b", "a/c"]
        to_paths = ["a/b", "a/c"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full_wrong,
            from_paths=from_paths,
            to_paths=to_paths,
            overriding=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full_wrong)
        assert_tree_structure_basenode_root_attr(self.root_other_full_wrong)
        assert_tree_structure_node_root_generic(self.root_other_full_wrong)

    # merge_children
    def test_copy_nodes_from_tree_to_tree_merge_children(self):
        from_paths = ["e", "g", "h"]
        to_paths = ["a/bb/e", "a/bb/e/g", "a/bb/e/h"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/bb"]
        to_paths = ["a/b/bb"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full,
            from_paths=from_paths,
            to_paths=to_paths,
            merge_children=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full)
        assert_tree_structure_basenode_root_attr(self.root_other_full)
        assert_tree_structure_node_root_generic(self.root_other_full)

    def test_copy_nodes_from_tree_to_tree_merge_children_non_overriding(self):
        from_paths = ["e", "g", "h"]
        to_paths = ["a/b/e", "a/b/e/g", "a/b/e/h"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/b"]
        to_paths = ["a/b"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full,
            from_paths=from_paths,
            to_paths=to_paths,
            merge_children=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full)
        assert_tree_structure_basenode_root_attr(self.root_other_full)
        assert_tree_structure_node_root_generic(self.root_other_full)

    def test_copy_nodes_from_tree_to_tree_merge_children_non_overriding_error(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/c"]
        to_paths = ["a/c"]
        with pytest.raises(TreeError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other_full,
                from_paths=from_paths,
                to_paths=to_paths,
                merge_children=True,
            )
        assert str(exc_info.value).startswith("Error: Duplicate node with same path")

    # merge_leaves
    def test_copy_nodes_from_tree_to_tree_merge_leaves(self):
        from_paths = ["a"]
        to_paths = ["a/b/a"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
            merge_leaves=True,
        )
        assert (
            self.root_other.max_depth == 3
        ), f"Depth is wrong, expected 3, received {self.root_other.depth}"
        assert [node.name for node in find_path(self.root_other, "a/b").children] == [
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
        ], "Nodes are not copied"

    def test_copy_nodes_from_tree_to_tree_merge_leaves_non_overriding(self):
        from_paths = ["a/e", "a/g", "a/h"]
        to_paths = ["/a/b/e", "a/c/g", "a/c/h"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/b", "a/c"]
        to_paths = ["/a/b", "a/b/e/c"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full,
            from_paths=from_paths,
            to_paths=to_paths,
            merge_leaves=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full)
        assert_tree_structure_basenode_root_attr(self.root_other_full)
        assert_tree_structure_node_root_generic(self.root_other_full)

    def test_copy_nodes_from_tree_to_tree_merge_leaves_non_overriding_error(self):
        from_paths = ["a/d", "a/e", "a/g", "a/h"]
        to_paths = ["a/b/d", "/a/b/e", "a/c/g", "a/c/h"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/b", "a/c"]
        to_paths = ["/a/b", "a/b/e/c"]

        with pytest.raises(TreeError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other_full,
                from_paths=from_paths,
                to_paths=to_paths,
                merge_leaves=True,
            )
        assert str(exc_info.value).startswith("Error: Duplicate node with same path")

    # delete_children
    def test_copy_nodes_from_tree_to_tree_delete_children(self):
        from_paths = ["a/b", "a/c", "a/d", "a/f"]
        to_paths = ["a/e/b", "a/e/b/c", "a/g/d", "a/h/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/e", "a/g", "a/h"]
        to_paths = ["/a/b/e", "a/b/e/g", "a/b/e/h"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full,
            from_paths=from_paths,
            to_paths=to_paths,
            delete_children=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full)
        assert_tree_structure_basenode_root_attr(self.root_other_full)
        assert_tree_structure_node_root_generic(self.root_other_full)

    # merge_children, overriding
    def test_copy_nodes_from_tree_to_tree_merge_children_overriding(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/bb/d", "a/bb/e", "a/bb/e/g", "a/bb/e/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/bb", "a/c"]
        to_paths = ["a/b/bb", "a/c"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full_wrong,
            from_paths=from_paths,
            to_paths=to_paths,
            merge_children=True,
            overriding=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full_wrong)
        assert_tree_structure_basenode_root_attr(self.root_other_full_wrong)
        assert_tree_structure_node_root_generic(self.root_other_full_wrong)

    # merge_leaves, overriding
    def test_copy_nodes_from_tree_to_tree_merge_leaves_overriding(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/bb/d", "a/bb/e", "a/cc/g", "a/cc/h", "a/c/f"]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/bb", "a/cc", "a/c"]
        to_paths = ["a/b/bb", "a/b/e/cc", "a/c"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full_wrong,
            from_paths=from_paths,
            to_paths=to_paths,
            merge_leaves=True,
            overriding=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full_wrong)
        assert_tree_structure_basenode_root_attr(self.root_other_full_wrong, c=("c", 1))
        assert_tree_structure_node_root_generic(self.root_other_full_wrong)

    # merge_children, merge_leaves
    def test_copy_nodes_from_tree_to_tree_merge_children_and_leaf_error(self):
        from_paths = ["a"]
        to_paths = ["a"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other_full_wrong,
                from_paths=from_paths,
                to_paths=to_paths,
                merge_children=True,
                merge_leaves=True,
            )
        assert str(exc_info.value).startswith(
            "Invalid shifting, can only specify one type of merging"
        )

    # merge_children, delete_children
    def test_copy_nodes_from_tree_to_tree_merge_children_and_delete_children(self):
        from_paths = ["e", "/b", "g", "/c", "h", "d", "f"]
        to_paths = [
            "a/bb/e",
            "a/bb/e/b",
            "a/cc/g",
            "a/cc/g/c",
            "a/cc/h",
            "a/cc/h/d",
            "a/cc/h/f",
        ]
        shift_nodes(self.root, from_paths, to_paths)

        from_paths = ["a/bb", "a/cc"]
        to_paths = ["a/b/bb", "a/b/e/cc"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other_full,
            from_paths=from_paths,
            to_paths=to_paths,
            merge_children=True,
            delete_children=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other_full)
        assert_tree_structure_basenode_root_attr(self.root_other_full)
        assert_tree_structure_node_root_generic(self.root_other_full)

    # with_full_path
    def test_copy_nodes_from_tree_to_tree_with_full_path(self):
        from_paths = ["a/b", "a/c", "a/d", "a/e", "a/f", "a/g", "a/h"]
        to_paths = ["a/b", "a/c", "a/b/d", "a/b/e", "a/c/f", "a/b/e/g", "a/b/e/h"]
        copy_nodes_from_tree_to_tree(
            from_tree=self.root,
            to_tree=self.root_other,
            from_paths=from_paths,
            to_paths=to_paths,
            with_full_path=True,
        )
        assert_tree_structure_basenode_root_generic(self.root_other)
        assert_tree_structure_basenode_root_attr(self.root_other)
        assert_tree_structure_node_root_generic(self.root_other)

    def test_copy_nodes_from_tree_to_tree_with_full_path_error(self):
        from_paths = ["d", "e", "g", "h", "f"]
        to_paths = ["a/b/d", "a/b/e", "a/b/e/g", "a/b/e/h", "a/c/f"]
        with pytest.raises(ValueError) as exc_info:
            copy_nodes_from_tree_to_tree(
                from_tree=self.root,
                to_tree=self.root_other,
                from_paths=from_paths,
                to_paths=to_paths,
                with_full_path=True,
            )
        assert str(exc_info.value).startswith(
            "Invalid path in `from_paths` not starting with the root node"
        )
