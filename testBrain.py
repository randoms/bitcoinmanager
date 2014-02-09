from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
import math
from pybrain.supervised.trainers import BackpropTrainer


#use sin function to test network

ds = SupervisedDataSet(1, 1)
for count in range(0,1000):
	inpt = count*0.01
	target = math.sin(inpt)
	ds.addSample((inpt,),(target,))

net = buildNetwork(1, 100, 1)
trainer = BackpropTrainer(net, ds)
trainer.trainUntilConvergence()

print net.acitve([2,])
