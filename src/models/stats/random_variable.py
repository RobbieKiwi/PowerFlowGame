from typing import TypeVar, Self, Callable

import numpy as np

from src.models.stats.models import Statistics
from src.models.stats.pdf_combiner import PdfCombiner
from src.models.stats.pdf_convolver import PdfConvolver
from .pdfs import *

__all__ = ["RandomVariable"]

T = TypeVar("T")


class RandomVariable:
    """
    The front door into the stats module
    """

    def __init__(self, pdf: ProbabilityDistributionFunction) -> None:
        self._pdf = pdf

    @property
    def pdf(self) -> ProbabilityDistributionFunction:
        return self._pdf

    @property
    def statistics(self) -> Statistics:
        return self.pdf.statistics

    def get_mean(self, exact: bool = False) -> float:
        return self.pdf.statistics.get(name="mean", certain=exact)

    def get_variance(self, exact: bool = False) -> float:
        return self.pdf.statistics.get(name="variance", certain=exact)

    def get_min_value(self, exact: bool = False) -> float:
        return self.pdf.statistics.get(name="min_value", certain=exact)

    def get_max_value(self, exact: bool = False) -> float:
        return self.pdf.statistics.get(name="max_value", certain=exact)

    def get_chance_that_rv_is_le(self, value: float, exact: bool = False) -> float:
        if exact and isinstance(self.pdf, EmpiricalDistributionFunction):
            raise ValueError("Exact CDF calculation is not supported for empirical distributions.")
        return self.pdf.chance_that_rv_is_le(value=value)

    def get_value_that_is_at_le_chance(self, chance: float, exact: bool = False) -> float:
        if exact and isinstance(self.pdf, EmpiricalDistributionFunction):
            raise ValueError("Exact quantile calculation is not supported for empirical distributions.")
        assert 0.0 <= chance <= 1.0, "Chance must be between 0 and 1."
        return self.pdf.value_that_is_at_le_chance(chance=chance)

    def sample_numpy(self, n: int) -> np.ndarray:
        return self.pdf.sample_numpy(n=n)

    def sample_one(self) -> float:
        return self.sample_numpy(1).tolist()[0]

    def add_special_event(self, value: float, chance: float) -> Self:
        assert 0 <= chance <= 1.0, "Value must be between 0 and 1"
        dirac_function = DiracDeltaDistributionFunction(value=value)
        new_pdf = PdfCombiner.combine_pdfs(pdfs=[self.pdf, dirac_function], chances=[1.0 - chance, chance])
        return RandomVariable(pdf=new_pdf)

    # TODO Add clip

    def __str__(self) -> str:
        mean = float(np.format_float_positional(x=self.statistics.mean.value, precision=3, fractional=False))
        var = float(np.format_float_positional(x=self.statistics.variance.value, precision=3, fractional=False))
        return f"<{self.__class__.__name__}: {mean=}, {var=}>"

    def __repr__(self) -> str:
        return str(self)

    def __add__(self, other: "RandomVariable") -> Self:
        # Assumes pdfs are not correlated
        assert isinstance(other, RandomVariable)
        new_pdf = PdfConvolver.convolve_pdfs(pdfs=[self.pdf, other.pdf])
        return RandomVariable(pdf=new_pdf)

    def __sub__(self, other: "RandomVariable") -> Self:
        # Assumes pdfs are not correlated
        assert isinstance(other, RandomVariable)
        return self + (other * -1)

    def __mul__(self, factor: float) -> Self:
        factor = float(factor)
        new_pdf = self.pdf.scale_x(other=factor)
        return RandomVariable(pdf=new_pdf)

    def __rmul__(self, factor: float) -> Self:
        return self.__mul__(factor)

    def __truediv__(self, factor: float) -> Self:
        return self.__mul__(1.0 / factor)

    @classmethod
    def make_dirac(cls, value: float) -> Self:
        return cls(pdf=DiracDeltaDistributionFunction(value=value))

    @classmethod
    def make_empirical(cls, sampler: Callable[[int], np.ndarray]) -> Self:
        return cls(pdf=EmpiricalDistributionFunction(sampler=sampler))

    @classmethod
    def make_normal(cls, mean: float, std_dev: float) -> Self:
        return cls(pdf=NormalDistributionFunction(mean=mean, std_dev=std_dev))

    @classmethod
    def make_uniform(cls, low: float, high: float) -> Self:
        return cls(pdf=UniformDistributionFunction(low=low, high=high))
