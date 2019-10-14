from veroviz._common import *
from veroviz._validation import valGenerateNodes
from veroviz._validation import valCreateNodesFromLocs

from veroviz._getSnapLoc import privGetSnapLocBatch
from veroviz._createEntitiesFromList import privCreateNodesFromLocs
from veroviz._internal import randomPick
from veroviz._internal import areaOfTriangle

from veroviz._geometry import geoDistance2D
from veroviz._geometry import geoIsPointInPoly
from veroviz._geometry import geoPointInDistance2D

from veroviz.utilities import initDataframe
from veroviz.utilities import getMapBoundary


def generateNodes(initNodes=None, nodeType=None, nodeName=None, numNodes=None, startNode=1, incrementName=False, incrementStart=1, nodeDistrib=None, nodeDistribArgs=None, snapToRoad=False, leafletIconPrefix=VRV_DEFAULT_LEAFLETICONPREFIX, leafletIconType=VRV_DEFAULT_LEAFLETICONTYPE, leafletColor=VRV_DEFAULT_LEAFLETICONCOLOR, leafletIconText=None, cesiumIconType=VRV_DEFAULT_CESIUMICONTYPE, cesiumColor=VRV_DEFAULT_CESIUMICONCOLOR, cesiumIconText=None, dataProvider=None, dataProviderArgs=None):

	"""
	This function generates a collection of nodes (locations).

	Parameters
	----------
	initNodes: :ref:`Nodes`, Optional, default as None
		A :ref:`Nodes` dataframe containing an existing set of nodes. If `initNodes` is provided, this function will append to that dataframe.
	nodeType: string, Optional, default as None
		A user-defined text field that can be used to classify nodes. This field is to categorize a batch of nodes (e.g., "warehouses"). If provided, all nodes generated by the `generateNodes()` function call will be given this value. The nodeType is not used by VeRoViz explicitly. 
	nodeName: string, Optional, default as None
		The name of all nodes that are to be generated by this function call. This field is a more detailed description (e.g., "Buffalo WH" or "Berlin WH"). The nodeName is not used by VeRoViz explicitly.  If provided, all nodes will use this nodeName.  See the `incrementName` flag below.
	numNodes: int, Required, default as None
		The number of nodes to be created.
	startNode: int, Optional, default as 1
		Specifies the starting node number.  This will be the maximum of startNode and any id values contained in the `id` column of the `initNodes` dataframe (if provided).  
	incrementName: boolean, Optional, default as False
		If this flag is set to `True, a unique integer value will be appended to the `nodeName`.  For example, if `nodeName = 'WH'` and `incrementName = True`, then the effective node names for 3 nodes would be 'WH1', 'WH2', and 'WH3'.
	incrementStart: int, Optional, default as 1
		The starting number of the nodeName increment.  See the `nodeName` and `incrementName` parameters above.
	nodeDistrib: string, Required, default as None
		Specifies a distribution by which the nodes will be generated.  See the table in the notes below for more information.
	nodeDistribArgs: dictionary, Required, default as None
		A dictionary of arguments for the distribution. See the table in the notes below for more information.
	snapToRoad: boolean, Optional, default as False, 
		If True, nodes will be positioned at locations on the road network. This requires the use of a data provider. See :ref:`Data Providers` for a list of data providers that support this option.
	leafletIconPrefix: string, Optional, default as "glyphicon"
		There are a large number of Leaflet icons available. The `leafletIconPrefix` identifies one of two collections: “glyphicon” or “fa”.  See :ref:`Leaflet Style` for more information.
	leafletIconType: string, Optional, default as "info-sign"
		Specifies the particular icon to be used for all generated nodes.  The list of available options depends on the choice of `leafletIconType`. See :ref:`Leaflet Style` for available options.
	leafletColor: string, Optional, default as "blue"
		Specifies the icon color of the generated nodes when displayed in Leaflet. See :ref:`Leaflet Style` for a list of available colors.
	leafletIconText: string, Optional, default as None
		Specifies the text in label that will be displayed when the node is clicked on a Leaflet map.  This parameter allows for including more information if the node name itself is not sufficiently descriptive.
	cesiumIconType: string, Optional, default as "pin"
		'pin' is current the only option. See :ref:`Cesium Style`.
	cesiumColor: string, Optional, default as "Cesium.Color.BLUE"
		The color of the generated nodes when displayed in Cesium.  See :ref:`Cesium Style` for all available color options.
	cesiumIconText: string, Optional, default as None
		Text that will be permanently displayed within the node on a Cesium map. If this field is None, in Cesium the node will be displayed with the `id` value. 
	dataProvider: string, Conditional, default as None
		Specifies the data source to be used for generating nodes on a road network. See :ref:`Data Providers` for options and requirements.
	dataProviderArgs: dictionary, Optional, default as None
		For some data providers, additional parameters are required (e.g., API keys or database names). See :ref:`Data Providers` for the additional arguments required for each supported data provider.

	Return
	------
	:ref:`Nodes`
		A :ref:`Nodes` dataframe of generated nodes.

	Note
	----
	VeRoViz currently supports the following distribution options.  For each distribution, specific additional parameters (arguments) must be provided in the `nodeDistribArgs` Python dictionary.

	+---------------------------+-------------------------------------------------------+
	| `nodeDistrib` Option      | Keys in `nodeDistribArgs` Dictionary                  |
	+===========================+=======================================================+
	| "uniformBB":              | 'boundingRegion' : A list of [lat,lon] pairs defines  | 
	| Uniformly distributed     | the boundary, in the form of [[lat1, lon1],           |
	| within a bounding region. | [lat2, lon2], ... , [latn, lonn]].                    |
	+---------------------------+-------------------------------------------------------+
	| "normal":                 | 'center' : Coordinate of center point, in form of     |
	| Normally distributed      | [lat, lon].                                           |
	| with a given center       |                                                       |
	| location and standard     +-------------------------------------------------------+
	| deviation. This option    | 'stdDev' : Standard deviation in meters               |
	| does not require a        | (70% nodes are within this range)                     |
	| bounding region. If a     |                                                       |
	| boundary is provided, it  |                                                       | 
	| will be regarded as       |                                                       |
	|  "normalBB".              |                                                       |
	+---------------------------+-------------------------------------------------------+
	| "normalBB":               | 'center' : Coordinate of center point, in form of     |
	| Truncated normally        | [lat, lon].                                           |
	| distributed with a        |                                                       |
	| given center location     +-------------------------------------------------------+
	| and standard deviation.   | 'stdDev' : Standard deviation, in meters              |
	|                           | (roughly 70% of nodes are within this range)          |
	|                           +-------------------------------------------------------+
	|                           | 'boundingRegion' : A list of lat/lon defines the      |
	|                           | boundary, in the form of [[lat, lon], [lat, lon],     |
	|                           | ... , [lat, lon]]                                     |
	+---------------------------+-------------------------------------------------------+

	Examples
	--------
	First import veroviz and check if it is the latest version:
	    >>> import veroviz as vrv
	    >>> vrv.checkVersion()

	This first example will generate 20 nodes, normally distributed. The distribution is centered at lat 42.30, lon 78.00. The distribution has a standard deviation of 1000 meters.
	    >>> myNodes = vrv.generateNodes(
	    ...     numNodes        = 20,
	    ...     nodeType        = 'depot', 
	    ...     nodeDistrib     = 'normal', 
	    ...     nodeDistribArgs = {
	    ...         'center' : [42.30, -78.00], 
	    ...         'stdDev' : 1000
	    ...     })
	    >>> myNodes

	View the center point, 1 std dev, 3 std devs, and resulting nodes on a Leaflet map:
	    >>> myMap = vrv.addLeafletMarker(center      = [42.30, -78.00], 
	    ...                              fillOpacity = 1)
	    >>> myMap = vrv.addLeafletCircle(mapObject = myMap, 
	    ...                              center    = [42.30, -78.00], 
	    ...                              radius    = 1000, 
	    ...                              fillColor = 'green')
	    >>> myMap = vrv.addLeafletCircle(mapObject = myMap, 
	    ...                              center    = [42.30, -78.00], 
	    ...                              radius    = 3*1000)
	    >>> myMap = vrv.createLeaflet(mapObject = myMap, 
	    ...                           nodes     = myNodes)
	    >>> myMap

	The following examples require a bounding region. For example:
	    >>> bounding = [
	    ...     [42.98355351219673, -78.90518188476564], 
	    ...     [43.04731443361136, -78.83857727050783], 
	    ...     [43.02221961002041, -78.7108612060547], 
	    ...     [42.92777124914475, -78.68957519531251], 
	    ...     [42.866402688514626, -78.75343322753908], 
	    ...     [42.874957707517865, -78.82415771484375], 
	    ...     [42.90111863978987, -78.86878967285158], 
	    ...     [42.92224052343343, -78.8921356201172]]

	The second example will give us 20 nodes, normally-distributed, centered at [42.30, 78.00], with a standard deviation of 2000 meters about the center.  However, the nodes must also fall within the bounding region.
	    >>> myNodes2 = vrv.generateNodes(
	    ...     numNodes        = 20,
	    ...     nodeType        = 'depot', 
	    ...     nodeDistrib     = 'normal', 
	    ...     nodeDistribArgs = {
	    ...         'center' : [42.90, -78.80], 
	    ...         'stdDev' : 2000,
	    ...         'boundingRegion' : bounding
	    ...     })
	    >>> myNodes2

	View the center point, 1 std dev, 3 std devs, bounding region, and resulting nodes on a Leaflet map:
		>>> myMap2 = vrv.addLeafletMarker(center      = [42.90, -78.80], 
		...                               fillOpacity = 1)
		>>> myMap2 = vrv.addLeafletCircle(mapObject = myMap2, 
		...                               center    = [42.90, -78.80], 
		...                               radius    = 4000, 
		...                               fillColor = 'green')
		>>> myMap2 = vrv.addLeafletCircle(mapObject = myMap2, 
		...                               center    = [42.90, -78.80], 
		...                               radius    = 3*4000)
		>>> myMap2 = vrv.createLeaflet(mapObject      = myMap2, 
		...                            nodes          = myNodes2,
		...                            boundingRegion = bounding)
		>>> myMap2

	The third example will generate 20 nodes uniformly distributed in a given bounding region:
	    >>> myNodes3 = vrv.generateNodes(
	    ...     numNodes        = 20, 
	    ...     nodeDistrib     = 'uniformBB', 
	    ...     nodeDistribArgs = {
	    ...         'boundingRegion' : bounding
	    ...     })
	    >>> myNodes3

	View the bounding region and generated nodes on a Leaflet map:
		>>> myMap3 = vrv.createLeaflet(nodes          = myNodes3,
		...                            boundingRegion = bounding)
		>>> myMap3

	The final example includes all available function arguments:
		>>> myNodes4 = vrv.generateNodes(
		...     initNodes         = None,
		...     nodeType          = 'warehouse',
		...     nodeName          = 'WH ',  
		...     numNodes          = 5,
		...     startNode         = 101,
		...     incrementName     = True,
		...     incrementStart    = 1,
		...     nodeDistrib       = 'uniformBB',
		...     nodeDistribArgs   = {
		...         'boundingRegion' : bounding
		...     },
		...     snapToRoad        = True,
		...     leafletIconPrefix = 'fa',
		...     leafletIconType   = 'star',
		...     leafletColor      = 'darkred',
		...     leafletIconText   = 'These nodes are used for demo',
		...     cesiumIconType    = 'pin',
		...     cesiumColor       = 'Cesium.Color.DARKRED',
		...     cesiumIconText    = None,
		...     dataProvider      = 'OSRM-online',
		...     dataProviderArgs  = None)
		>>> myNodes4	    

	View the bounding region and generated nodes on a Leaflet map:
		>>> myMap4 = vrv.createLeaflet(nodes          = myNodes4,
		...                            boundingRegion = bounding)
		>>> myMap4
	"""

	# validation
	[valFlag, errorMsg, warningMsg] = valGenerateNodes(initNodes, nodeType, nodeName, numNodes, startNode, incrementName, incrementStart, nodeDistrib, nodeDistribArgs, snapToRoad, leafletIconPrefix, leafletIconType, leafletColor, leafletIconText, cesiumIconType, cesiumColor, cesiumIconText, dataProvider, dataProviderArgs)
	if (not valFlag):
		print (errorMsg)
		return
	elif (VRV_SETTING_SHOWWARNINGMESSAGE and warningMsg != ""):
		print (warningMsg)

	# Generate random nodes - For 2D nodes
	if (nodeDistrib == "uniformBB"):
		boundingRegion = nodeDistribArgs['boundingRegion']
		locs = _genNodesUniformBounded(numNodes, boundingRegion)		
	elif (nodeDistrib == "normal"):
		if ('boundingRegion' not in nodeDistribArgs):
			center = nodeDistribArgs['center']
			standardDeviation = nodeDistribArgs['stdDev']
			locs = _genNodesNormal(numNodes, center, standardDeviation)
		else:
			boundingRegion = nodeDistribArgs['boundingRegion']
			center = nodeDistribArgs['center']
			standardDeviation = nodeDistribArgs['stdDev']
			locs = _genNodesNormalBounded(numNodes, boundingRegion, center, standardDeviation)
	elif (nodeDistrib == "normalBB"):
		boundingRegion = nodeDistribArgs['boundingRegion']
		center = nodeDistribArgs['center']
		standardDeviation = nodeDistribArgs['stdDev']
		locs = _genNodesNormalBounded(numNodes, boundingRegion, center, standardDeviation)
	elif (nodeDistrib == "unifRoadBasedBB"):
		boundingRegion = nodeDistribArgs['boundingRegion']
		distToRoad = nodeDistribArgs['distToRoad']
		locs = _genNodesRoadBased(numNodes, boundingRegion, distToRoad, dataProvider, dataProviderArgs)

	# create nodes from given lats/lons
	nodes = privCreateNodesFromLocs(locs, initNodes, nodeType, nodeName, startNode, incrementName, incrementStart, snapToRoad, dataProvider, dataProviderArgs, leafletIconPrefix, leafletIconType, leafletColor, leafletIconText, cesiumIconType, cesiumColor, cesiumIconText)
	return nodes

def _genNodesUniformBounded(numNodes=None, boundingRegion=None):
	"""
	Generate randomized node using Uniform distribution within a bounding area

	Note
	----
	This function is an approximation, the error is getting larger when the location is closer to poles

	Parameters
	----------
	numNodes: int, Required
		Number of nodes to be generated
	boudingArea: list, Required
		A defined polygon, nodes are generated within this area

	Returns
	-------
	list of lists
		A list of coordinates uniformly distributed with bounding region
	"""

	# Use polygon triangulation to cut the bounding region into a list of triangules, calculate the area of each triangle
	lstTriangle = tripy.earclip(boundingRegion)
	lstArea = []
	for i in range(len(lstTriangle)):
		lstArea.append(areaOfTriangle(lstTriangle[i][0], lstTriangle[i][1], lstTriangle[i][2]))
	
	# Randomly pick a triangle, the probability of picking triangle is refer to the area of each triangle, then generate one node inside, loop untill generate enough nodes
	locs = []
	for i in range(numNodes):
		index = randomPick(lstArea)
		newLoc = _genNodesUniformTriangle(1, lstTriangle[index])
		locs.extend(newLoc)

	return locs

def _genNodesUniformTriangle(numNodes=None, triangle=None):
	"""
	Generate randomized node using Uniform distribution within a triangle

	Note
	----
	This function is an approximation, the error is getting larger when the location is closer to poles

	Parameters
	----------
	numNodes: int, Required
		Number of nodes to be generated
	triangle: list, Required
		A defined triangle, format is [[lat1, lon1], [lat2, lon2], [lat3, lon3]]

	Returns
	-------
	list of lists
		A list of coordinates randomly generated at given triangle
	"""

	# Give number to three vertices of triangle
	[lat1, lon1] = triangle[0]
	[lat2, lon2] = triangle[1]
	[lat3, lon3] = triangle[2]

	# initialize lists
	locs = []
	# Generate random nodes
	# Reference: http://www.cs.princeton.edu/~funk/tog02.pdf
	for i in range(numNodes):
		rndR1 = np.random.uniform(0, 1)
		rndR2 = np.random.uniform(0, 1)
		rndLat = (1 - math.sqrt(rndR1)) * lat1 + math.sqrt(rndR1) * (1 - rndR2) * lat2 + math.sqrt(rndR1) * rndR2 * lat3
		rndLon = (1 - math.sqrt(rndR1)) * lon1 + math.sqrt(rndR1) * (1 - rndR2) * lon2 + math.sqrt(rndR1) * rndR2 * lon3
		locs.append([rndLat, rndLon])

	return locs

def _genNodesNormalBounded(numNodes=None, boundingRegion=None, center=None, standardDeviation=None):

	"""
	Generate randomized node using Normal distribution within a bounding area

	Parameters
	----------
	numNodes: int, Required
		Number of nodes to be generated
	boudingArea: list, Required
		A defined polygon, nodes are generated within this area
	centerLat: float, Required
		Latitude of the center point
	centerLon: float, Required
		Longitude of the center point
	standardDeviation: float, Required
		StandardDeviation of normal distribution

	Return
	------
	list of lists
		A list of coordinates uniformly distributed within a bounding area
	"""

	# Initialize
	locs = []

	# Randomized generate nodes in normal distribution
	for i in range(numNodes):
		rndUniform = np.random.uniform(0, 360)
		rndNormal = np.random.normal(0, standardDeviation)
		newLoc = geoPointInDistance2D(center, rndUniform, rndNormal)
		while (not geoIsPointInPoly(newLoc, boundingRegion)):
			rndUniform = np.random.uniform(0, 360)
			rndNormal = np.random.normal(0, standardDeviation)
			newLoc = geoPointInDistance2D(center, rndUniform, rndNormal)
		locs.append(newLoc)
		
	return locs

def _genNodesNormal(numNodes=None, center=None, standardDeviation=None):
	"""
	Generate randomized node using Normal distribution within a bounding area

	Parameters
	----------
	numNodes: int
		Required, number of nodes to be generated
	centerLat: float, Required
		Latitude of the center point
	centerLon: float, Required
		Longitude of the center point
	standardDeviation: float, Required
		StandardDeviation of normal distribution

	Returns
	-------
	list of lists
		A list of coordinates uniformly distributed
	"""

	# Initialize
	locs = []

	# Randomized generate nodes in normal distribution
	for i in range(numNodes):
		rndUniform = np.random.uniform(0, 360)
		rndNormal = np.random.normal(0, standardDeviation)
		newLoc = geoPointInDistance2D(center, rndUniform, rndNormal)
		locs.append(newLoc)
		
	return locs

def _genNodesRoadBased(numNodes=None, boundingRegion=None, distToRoad=None, dataProvider=None, APIkey=None, databaseName=None):
	"""
	Generate randomized node using Uniform distribution within a bounding area and close to roads

	Note
	----
	This function is an approximation, the error is getting larger when the location is closer to poles

	Parameters
	----------
	numNodes: int, Required
		Number of nodes to be generated
	boudingArea: list, Required
		A defined polygon, nodes are generated within this area
	distToRoad: float, Required
		The maximun distance to road for generated nodes.
	dataProvider: string, Conditional, See :ref:`Dataprovider`
		Specifies the data source to be used for generating nodes on a road network.  
	APIkey: string, Conditional, See :ref:`Dataprovider`
		Some data providers require an API key (which you'll need to register for).
	databaseName: string, Conditional, See :ref:`Dataprovider`
		If you are hosting a data provider on your local machine (e.g., pgRouting), you'll need to specify the name of the local database. 
	
	Returns
	-------
	list of lists
		A list of coordinates, within a given distance to its nearest street
	"""

	# Initialize
	locs = []

	# Generate nodes, if it is not close enough, discard and regenerate
	while (len(locs) < numNodes):
		newLocs = _genNodesUniformBounded(numNodes - len(locs), boundingRegion)
		snapLocs = privGetSnapLocBatch(newLocs, dataProvider, APIkey, databaseName)
		for i in range(len(snapLocs)):
			if (geoDistance2D(newLocs[i], snapLocs[i]) <= distToRoad):
				locs.append(newLocs[i])
	
	return locs

def createNodesFromLocs(locs=None, initNodes=None, nodeType=None, nodeName=None, startNode=1, incrementName=False, incrementStart=1, snapToRoad=False, dataProvider=None, dataProviderArgs=None, leafletIconPrefix=VRV_DEFAULT_LEAFLETICONPREFIX, leafletIconType=VRV_DEFAULT_LEAFLETICONTYPE, leafletColor=VRV_DEFAULT_LEAFLETICONCOLOR, leafletIconText=None, cesiumIconType=VRV_DEFAULT_CESIUMICONTYPE, cesiumColor=VRV_DEFAULT_CESIUMICONCOLOR, cesiumIconText=None):

	"""
	This function generates a "nodes" dataframe from a given collection of [lat, lon], or [lat, lon, alt], coordinates.

	Parameters
	----------
	locs: list of lists, Required, default as None
		A list of locations, in the form of [[lat, lon, alt], [lat, lon, alt], ...] or [[lat, lon], [lat, lon], ...].  If no altitudes are provided, all will be assumed to be 0 meters above ground level.
	initNodes: :ref:`Nodes`, Optional, default as None
		A :ref:`Nodes` dataframe containing an existing set of nodes. If `initNodes` is provided, this function will append to that dataframe.
	nodeType: string, Optional, default as None
		A user-defined text field that can be used to classify nodes. This field is to categorize a batch of nodes (e.g., "warehouses"). If provided, all nodes generated by the `generateNodes()` function call will be given this value. The nodeType is not used by VeRoViz explicitly. 
	nodeName: string, Optional, default as None
		The name of all nodes that are to be generated by this function call. This field is a more detailed description (e.g., "Buffalo WH" or "Berlin WH"). The nodeName is not used by VeRoViz explicitly.  If provided, all nodes will use this nodeName.  See the `incrementName` flag below.
	startNode: int, Optional, default as 1
		Specifies the starting node number.  This will be the maximum of startNode and any id values contained in the `id` column of the `initNodes` dataframe (if provided).  
	incrementName: boolean, Optional, default as False
		If this flag is set to `True, a unique integer value will be appended to the `nodeName`.  For example, if `nodeName = 'WH'` and `incrementName = True`, then the effective node names for 3 nodes would be 'WH1', 'WH2', and 'WH3'.
	incrementStart: int, Optional, default as 1
		The starting number of the nodeName increment.  See the `nodeName` and `incrementName` parameters above.
	snapToRoad: boolean, Optional, default as False, 
		If True, nodes will be positioned at locations on the road network. This requires the use of a data provider. See :ref:`Data Providers` for a list of data providers that support this option.
	dataProvider: string, Conditional, default as None
		Specifies the data source to be used for generating nodes on a road network. See :ref:`Data Providers` for options and requirements.
	dataProviderArgs: dictionary, Optional, default as None
		For some data providers, additional parameters are required (e.g., API keys or database names). See :ref:`Data Providers` for the additional arguments required for each supported data provider.
	leafletIconPrefix: string, Optional, default as "glyphicon"
		There are a large number of Leaflet icons available. The `leafletIconPrefix` identifies one of two collections: “glyphicon” or “fa”.  See :ref:`Leaflet Style` for more information.
	leafletIconType: string, Optional, default as "info-sign"
		Specifies the particular icon to be used for all generated nodes.  The list of available options depends on the choice of `leafletIconType`. See :ref:`Leaflet Style` for available options.
	leafletColor: string, Optional, default as "blue"
		Specifies the icon color of the generated nodes when displayed in Leaflet. See :ref:`Leaflet Style` for a list of available colors.
	leafletIconText: string, Optional, default as None
		Specifies the text in label that will be displayed when the node is clicked on a Leaflet map.  This parameter allows for including more information if the node name itself is not sufficiently descriptive.
	cesiumIconType: string, Optional, default as "pin"
		'pin' is current the only option. See :ref:`Cesium Style`.
	cesiumColor: string, Optional, default as "Cesium.Color.BLUE"
		The color of the generated nodes when displayed in Cesium.  See :ref:`Cesium Style` for all available color options.
	cesiumIconText: string, Optional, default as None
		Text that will be permanently displayed within the node on a Cesium map. If this field is None, in Cesium the node will be displayed with the `id` value. 


	Returns
	-------
	:ref:`Nodes` dataframe
		A :ref:`Nodes` dataframe generated from the given list of coordinates.


	Examples
	--------

	Import veroviz and check if it is the latest version:
	    >>> import veroviz as vrv
	    >>> vrv.checkVersion()
	    
	    
	Generate nodes from a list of [lat, lon] pairs (no altitude specified):
		>>> nodes2D = vrv.createNodesFromLocs(
		...     locs=[
		...         [42.1538, -78.4253],
		...         [42.3465, -78.6234],
		...         [42.6343, -78.1146]])
		>>> nodes2D

	Generate nodes from a list of [lat, lon, alt] pairs:
		>>> nodes3D = vrv.createNodesFromLocs(
		...     locs=[
		...         [42.1538, -78.4253, 200],
		...         [42.3465, -78.6234, 400],
		...         [42.6343, -78.1146, 200]])
		>>> nodes3D

	This example includes all function arguments:
		>>> myLocs = [[42.1538, -78.4253],
		...           [42.3465, -78.6234],
		...           [42.6343, -78.1146]]
		>>> myNodes = vrv.createNodesFromLocs(
		...     locs              = myLocs, 
		...     initNodes         = None, 
		...     nodeType          = 'customers', 
		...     nodeName          = 'cust', 
		...     startNode         = 1, 
		...     incrementName     = True, 
		...     incrementStart    = 7, 
		...     snapToRoad        = False, 
		...     dataProvider      = None, 
		...     dataProviderArgs  = None,
		...     leafletIconPrefix = 'fa', 
		...     leafletIconType   = 'user', 
		...     leafletColor      = 'lightgreen', 
		...     leafletIconText   = None, 
		...     cesiumIconType    = 'pin', 
		...     cesiumColor       = 'Cesium.Color.LIGHTGREEN', 
		...     cesiumIconText    = None)
		>>> myNodes

	Display the nodes on a Leaflet map:
		>>> vrv.createLeaflet(nodes = nodes2D)
	"""

	# validation
	[valFlag, errorMsg, warningMsg] = valCreateNodesFromLocs(locs, initNodes, nodeType, nodeName, startNode, incrementName, incrementStart, snapToRoad, dataProvider, dataProviderArgs, leafletIconPrefix, leafletIconType, leafletColor, leafletIconText, cesiumIconType, cesiumColor, cesiumIconText)
	if (not valFlag):
		print (errorMsg)
		return
	elif (VRV_SETTING_SHOWWARNINGMESSAGE and warningMsg != ""):
		print (warningMsg)

	nodes = privCreateNodesFromLocs(locs, initNodes, nodeType, nodeName, startNode, incrementName, incrementStart, snapToRoad, dataProvider, dataProviderArgs, leafletIconPrefix, leafletIconType, leafletColor, leafletIconText, cesiumIconType, cesiumColor, cesiumIconText)

	return nodes