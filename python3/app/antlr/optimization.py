from lib.hash import ValueFactorHashCodeCombiner
from antlr4.atn.ATNConfigSet import ATNConfigSet


def hash_atnconfigset(self):
    hash_ = ValueFactorHashCodeCombiner.make()
    for cfg in self.configs:
        hash_.put(cfg)
    return hash_.value


ATNConfigSet.hashConfigs = hash_atnconfigset


