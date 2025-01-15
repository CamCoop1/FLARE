import b2luigi as luigi

from analysis.tasks import AnalysisPlot

if __name__ == "__main__":
    luigi.process(AnalysisPlot(), workers=4)
