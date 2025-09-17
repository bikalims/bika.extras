# -*- coding: utf-8 -*-


def getNumberOfSamples(self):
    """
    Returns the number of samples.
    :returns: number of samples
    :rtype: integer
    """
    samples = self.getAnalysisRequests()
    return len(samples)
