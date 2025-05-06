# Beautiful Trains Package Overview
**Beautiful Trains** aims to abstract metro rapid transit networks into a set of python data structures, with the aim of identifying and visualizing low cost performance improvements to said networks.

The long term vision is to have a set of code which accepts an arbitrary city from a list of cities verified to have the relevant data and produce relevant ways to improve the local transportation network.

The current project focus is on rail based transportation in Chicago, IL, USA. The current question this code aims to answer is:

***Which two currently unconnected "L" stations, if connected, would decrease the average commute length (measured in # of stations) maximally when weighted by the number of rides?***
****
The core innovation that enables this analysis to be done is the abstraction of an interconnected rail network into a mathematical graph. 
NetworkX is used to do this abstraction.

***rt_network*** is a package of objects meant to be layered on top of one another which provide intuitive structure to the network. 
There is a data structure for stations and connections, which come together to form "Lines," which in turn come together to form the full network.

This structure allows metadata to be stored about each layer of the network and for functions or behaviors related to that metadata to be encoded directly into the object. 
The networks are then pickled and stored locally for quick analysis. 
We build the network once, and then rely on the stored information to make asking questions about the network more efficient.

****

In the future, the plan is to incorporate bus stops into the network (which will be flagged at the "Station" level in the data) as well as determining how well the overall network is serving the community by measuring access to transportation, wait times, travel times when compared to car travel times.
This will involve looking at GIS data about housing, traffic data, geological and weather data, demographic data, etc. and will necessarily include some interesting statistics in the fields of queuing theory, different types of forecasting and much more.

The hope is that this will eventually provide cost-effective and reliable blueprints for cities to improve their transportation infrastructure.
Urban and rural citizens alike need access to affordable and reliable transportation to seek economic opportunity and will hopefully both benefit from this work.
