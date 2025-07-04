import numpy as np

from src.models.stats.models import Statistics, sum_uncertain_floats
from src.models.stats.pdfs.base import (
    ProbabilityDistributionFunction,
    T_Pdf,
)
from src.models.stats.pdfs.dirac import DiracDeltaDistributionFunction
from src.models.stats.pdfs.empirical import EmpiricalDistributionFunction
from src.models.stats.pdfs.normal import NormalDistributionFunction
from src.models.stats.pdfs.uniform import UniformDistributionFunction


class PdfConvolver:
    @classmethod
    def convolve_pdfs(cls, pdfs: list[ProbabilityDistributionFunction]) -> ProbabilityDistributionFunction:
        assert len(pdfs) >= 2, "At least two PDFs are required for combination."
        if not all(isinstance(pdf, ProbabilityDistributionFunction) for pdf in pdfs):
            types = {pdf.__class__.__name__ for pdf in pdfs}
            raise TypeError(f"All PDFs must be instances of ProbabilityDistributionFunction, got: {types}")

        if all(isinstance(rv, NormalDistributionFunction) for rv in pdfs):
            return cls.convolve_normals(pdfs=pdfs)  # type: ignore

        if len(pdfs) == 2 and any(isinstance(rv, DiracDeltaDistributionFunction) for rv in pdfs):
            pdf_a, dirac = pdfs[0], pdfs[1]
            if isinstance(pdf_a, DiracDeltaDistributionFunction):
                pdf_a, dirac = dirac, pdf_a
            return cls.convolve_with_dirac_delta(pdf_a=pdf_a, dirac=dirac)

        return cls.convolve_empirical(pdfs=pdfs)

    @classmethod
    def convolve_normals(cls, pdfs: list[NormalDistributionFunction]) -> NormalDistributionFunction:
        # Equivalent to adding independent normal random variables
        if not pdfs:
            raise ValueError("No PDFs provided for combination.")

        for pdf in pdfs:
            assert isinstance(pdf, NormalDistributionFunction)

        new_mean = sum([pdf.mean for pdf in pdfs])
        new_variance = sum([pdf.variance for pdf in pdfs])
        return NormalDistributionFunction(mean=new_mean, std_dev=new_variance**0.5)

    @classmethod
    def convolve_with_dirac_delta(cls, pdf_a: T_Pdf, dirac: DiracDeltaDistributionFunction) -> T_Pdf:
        # Equivalent to adding a constant to the random variable
        assert isinstance(pdf_a, ProbabilityDistributionFunction)
        assert isinstance(dirac, DiracDeltaDistributionFunction)

        if isinstance(pdf_a, NormalDistributionFunction):
            new_mean = pdf_a.mean + dirac.mean
            return NormalDistributionFunction(mean=new_mean, std_dev=pdf_a.std_dev)
        if isinstance(pdf_a, UniformDistributionFunction):
            new_values = (pdf_a.min_value + dirac.mean, pdf_a.max_value + dirac.mean)
            new_low = min(new_values)
            new_high = max(new_values)
            return UniformDistributionFunction(low=new_low, high=new_high)
        if isinstance(pdf_a, DiracDeltaDistributionFunction):
            new_mean = pdf_a.mean + dirac.mean
            return DiracDeltaDistributionFunction(value=new_mean)
        raise NotImplementedError(f"Combination for pdf type {type(pdf_a)} is not implemented.")

    @classmethod
    def convolve_empirical(cls, pdfs: list[ProbabilityDistributionFunction]) -> EmpiricalDistributionFunction:
        if not pdfs:
            raise ValueError("No PDFs provided for combination.")

        for pdf in pdfs:
            assert isinstance(pdf, ProbabilityDistributionFunction)

        sum_unc = sum_uncertain_floats

        stats = [pdf.statistics for pdf in pdfs]
        mean = sum_unc([s.mean for s in stats])
        variance = sum_unc([s.variance for s in stats])

        min_value = sum_unc([s.min_value for s in stats])
        max_value = sum_unc([s.max_value for s in stats])
        min_value, max_value = sorted([min_value, max_value], key=lambda x: x.value)

        statistics = Statistics(mean=mean, variance=variance, min_value=min_value, max_value=max_value)

        def sampler(n: int) -> np.ndarray:
            samples = [p.sample_numpy(n) for p in pdfs]
            return np.sum(samples, axis=0)

        return EmpiricalDistributionFunction(sampler=sampler, n_samples=5000, statistics=statistics)
