from src.models.stats.pdf_combiner import PdfCombiner
from src.models.stats.pdfs import DiracDeltaDistributionFunction
from src.models.stats.random_variable import RandomVariable


if __name__ == "__main__":
    # Example usage
    from src.models.stats.pdfs.uniform import UniformDistributionFunction

    uniform_pdf = UniformDistributionFunction(low=0.0, high=10.0)
    uniform_rv = RandomVariable(pdf=uniform_pdf)

    new_rv = add_special_event_to_rv(rv=uniform_rv, value=5.0, chance=0.2)
    print(new_rv.statistics)
    new_rv.pdf.plot()
