"""Few examples demonstration how to use sphinx to document code.
"""


def basicExample(a: int) -> int:
    """
    Short description
        Adds 1 to a

    Long Description
        Text of paragraph
        this is still on the same line.

        Start a new block in this paragraph

    This is the second paragraph see how I indented the first line of the new paragraph
    I can start a new line here.

    Args:
        a: integer to increment

    Returns:
        a incremented by one

    """

    return a + 1


def formatingExamples():
    """
    For an exhaustive list of formationg options refere to `sphinx <link_>`_

    .. _link: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
    """


def linksAndReferenceExample(a: int) -> int:
    """
    References
        This paper [ref1]_ describes how AlphaFold was developed. Refs [ref2]_ are shown in the documentation of the function.
        References can also be stored in a dedicated (`docs/references.rst`) and used here [Wagner2019]_. In contrast to links (see below) we
        need to include the dedicated document the build of the page.

    Links
        This is how to use links, `link1`_, link with custome name `hihi <link2_>`_.
        Link defined in other document `my link`_.

    .. _link1: https://www.nature.com/articles/s41586-021-03819-2
    .. _link2: https://www.nature.com/articles/s41586-021-03819-2
    .. [ref1] https://www.nature.com/articles/s41586-021-03819-2
    .. [ref2] https://google.com

    """
    pass


def formlasExample():
    """
    Example demonstrating how to use mathematical expressions. Keep in mind that when you put math markup in Python docstrings read by autodoc, you either have to double all backslashes, or use Python raw strings (r"raw").

    Inline
        Since Pythagoras, we know that :math:`a^2 + b^2 = c^2`.

    Equations
        Sphinx can render LaTeX typeset math in the browser.
        We have to add empty lines around the equation.
        And we have to be carefule with escaping \\f.

        .. math:: \int_0^a x\,dx = \\frac{1}{2}a^2

        We can also put multiple equation in one environment an align them. Remember to use double backslash when using ``autodoc``.

        .. math::

            e^{i\pi} + 1 &= ? \\\\
                         &= 0

    Options
        Set ``math_number_all`` option to True if you want all displayed math to be numbered. The default is False.

    Returns:
        None

    """
    pass


def codeExample():
    """
    Example demonstrating how to use code examples.

    Inline Snippets
        Short code snippets can be shown inline with ``code``.

    Code Blocks
        .. code-block:: python

            import numpy as np

            np.deg2rad(90)  # pi / 2
            np.rad2deg(np.pi / 2)  # 90.0

            Copy and Paste Output

    Console Output
        >>> 1 + 1
        2


    Examples
        Examples can be given using either the ``Example`` or ``Examples``
        sections. Sections support any reStructuredText formatting, including
        literal blocks. Literal code blocks (ref) are introduced by ending a
        paragraph with the special marker ::. The literal block must be indented
        (and, like all paragraphs, separated from the surrounding ones by blank lines)::

            $ python example_google.py

    Examples:
        Note the difference in appearnce depending on ``Example`` or ``Example:``

    """
    pass


class Boo:
    """
    Toy class to demonstrate cross-referencing.
    """

    a: int = 10

    def __init__(self):
        pass

    def foo(self):
        pass

    def _bar(self):
        pass


def crossReferencing():
    """
    Demonstration of cross-referencing to internal and external functions.

    Internal References
        We can reference
        methods with :meth:`codeExample`,
        classes with :class:`Boo`,
        class methods :meth:`Boo.foo`, but not if they are not visible :meth:`Boo._bar`,
        class attributes :attr:`Boo.a`.

    External References
        This can be cumbersome and is API dependent, for more see `here <link1_>`_ and `here <link2_>`_.
        Sometimes inspecting the inventory can help ``python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv``

        We can reference external documentations with the ``sphinx.ext.intersphinx`` extension and
        the required mappings specified in ``intersphinx_mapping`` in the `conf.py`.

        Reference pandas :class:`~pandas.core.frame.DataFrame` class or :class:`pandas.core.frame.DataFrame`
        Reference numpys

            - :class:`numpy.DataSource`, works
            - :c:enum:`NPY_CASTING`, works
            - :enum:`NPY_CASTING`, does not work,
            - :py:function::`numpy.all`, :py:meth:`numpy.all`, :py:method::`numpy.all`, does not work

        .. _link4: https://stackoverflow.com/questions/30939867/how-to-properly-write-cross-references-to-external-documentation-with-intersphin
        .. _link5: https://stackoverflow.com/questions/46080681/scikit-learn-intersphinx-link-inventory-object
    """
    pass
