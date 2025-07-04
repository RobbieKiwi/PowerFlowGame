import numpy as np

from src.models.stats.models import Uncertainty, Statistics, sum_uncertain_floats
from src.models.stats.pdfs import (
    ProbabilityDistributionFunction,
    DiracDeltaDistributionFunction,
    EmpiricalDistributionFunction,
)


class PdfCombiner:

    @classmethod
    def combine_pdfs(
        cls, pdfs: list[ProbabilityDistributionFunction], chances: list[float] | None = None, n_samples: int = 10000
    ) -> EmpiricalDistributionFunction:
        """
        In contrast to the pdf convovler, this class adds together the pdfs of different distributions
        The chance parameter describes the chance of each PDF being sampled.
        """
        assert len(pdfs) >= 2, "At least two PDFs are required for combination"
        assert all(isinstance(pdf, ProbabilityDistributionFunction) for pdf in pdfs)

        if chances is None:
            chances = [1.0 / len(pdfs)] * len(pdfs)
        assert len(pdfs) == len(chances), "Number of PDFs must match number of weights"
        assert all(w > 0 for w in chances), "All weights must be positive"
        total_weight = sum(chances)
        assert abs(total_weight - 1.0) < 1e-9, "Weights must sum to 1"

        def sampler(n: int) -> np.ndarray:
            pdf_choices = np.random.choice(len(pdfs), size=n, p=chances)

            samples = np.zeros(n)
            for i in range(len(pdfs)):
                # Get the number of samples to draw from this PDF
                num_samples = np.sum(pdf_choices == i)
                if num_samples > 0:
                    # Draw samples from the PDF and add them to the result
                    samples[pdf_choices == i] = pdfs[i].sample_numpy(num_samples)
            return samples

        mean = sum_uncertain_floats(pdf.statistics.mean * weight for pdf, weight in zip(pdfs, chances))

        extreme_values = [pdf.statistics.min_value for pdf in pdfs] + [pdf.statistics.max_value for pdf in pdfs]
        min_value = min(extreme_values, key=lambda x: x.value)
        max_value = max(extreme_values, key=lambda x: x.value)

        # TODO this could probably be solved analytically
        variance = Uncertainty(value=float(np.var(sampler(n_samples))), is_certain=False)

        stats = Statistics(
            mean=mean,
            variance=variance,
            min_value=min_value,
            max_value=max_value,
        )

        return EmpiricalDistributionFunction(sampler=sampler, n_samples=n_samples, statistics=stats)


if __name__ == "__main__":
    dirac1 = DiracDeltaDistributionFunction(value=1.0)
    dirac2 = DiracDeltaDistributionFunction(value=2.0)
    combined = PdfCombiner.combine_pdfs([dirac1, dirac2], chances=[0.5, 0.5])
    print(combined.statistics)
