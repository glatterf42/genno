import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Hashable, Sequence
from warnings import warn

import plotnine as p9

from genno.core.quantity import Quantity

if TYPE_CHECKING:
    from genno.core.computer import Computer
    from genno.core.key import KeyLike

log = logging.getLogger(__name__)


class Plot(ABC):
    """Class for plotting using :mod:`plotnine`."""

    #: Filename base for saving the plot.
    basename = ""
    #: File extension; determines file format.
    suffix = ".pdf"
    #: Keys for quantities needed by :meth:`generate`.
    inputs: Sequence[Hashable] = []
    #: Keyword arguments for :meth:`plotnine.ggplot.save`.
    save_args = dict(verbose=False)

    # TODO add static geoms automatically in generate()
    __static: Sequence = []

    def save(self, config, *args, **kwargs):
        """Prepare data, call :meth:`.generate`, and save to file.

        This method is used as the callable in the task generated by :meth:`.make_task`.
        """
        path = config["output_dir"] / f"{self.basename}{self.suffix}"

        missing = tuple(filter(lambda arg: isinstance(arg, str), args))
        if len(missing):
            log.error(
                f"Missing input(s) {missing!r} to plot {self.basename!r}; no output"
            )
            return

        # Convert Quantity arguments to pd.DataFrame for use with plotnine
        args = map(
            lambda arg: arg
            if not isinstance(arg, Quantity)
            else arg.to_series()
            .rename(arg.name or "value")
            .reset_index()
            .assign(unit=f"{arg.units:~}"),
            args,
        )

        plot_or_plots = self.generate(*args, **kwargs)

        if not plot_or_plots:
            log.info(
                f"{self.__class__.__name__}.generate() returned {plot_or_plots!r}; no "
                "output"
            )
            return

        log.info(f"Save to {path}")

        try:
            # Single plot
            plot_or_plots.save(path, **self.save_args)
        except AttributeError:
            # Iterator containing 0 or more plots
            p9.save_as_pdf_pages(plot_or_plots, path, **self.save_args)

        return path

    @classmethod
    def make_task(cls, *inputs):
        """Return a task :class:`tuple` to add to a Computer.

        .. deprecated:: 1.18.0

           Use :func:`add_tasks` instead.

        Parameters
        ----------
        inputs : sequence of :class:`.Key`, :class:`str`, or other hashable, optional
            If provided, overrides the :attr:`inputs` property of the class.

        Returns
        -------
        tuple
            - The first, callable element of the task is :meth:`save`.
            - The second element is ``"config"``, to access the configuration of the
              Computer.
            - The third and following elements are the `inputs`.
        """
        inputs_repr = ",".join(map(repr, inputs))
        warn(
            f"Plot.make_task(…). Use: Computer.add(…, {cls.__name__}"
            + (", " if inputs_repr else "")
            + f"{inputs_repr})",
            DeprecationWarning,
        )
        return tuple([cls().save, "config"] + (list(inputs) if inputs else cls.inputs))

    @classmethod
    def add_tasks(
        cls, c: "Computer", key: "KeyLike", *inputs, strict: bool = False
    ) -> "KeyLike":
        """Add a task to `c` to generate and save the Plot.

        Analogous to :meth:`.Operator.add_tasks`.
        """
        _inputs = list(inputs if inputs else cls.inputs)
        if strict:
            _inputs = c.check_keys(*_inputs)
        return c.add_single(key, cls().save, "config", *_inputs)

    @abstractmethod
    def generate(self, *args, **kwargs):
        """Generate and return the plot.

        Must be implemented by subclasses.

        Parameters
        ----------
        args : sequence of :class:`pandas.DataFrame`
            Because :mod:`plotnine` operates on pandas data structures, :meth:`save`
            automatically converts :obj:`Quantity` before being provided to
            :meth:`generate`.
        """
