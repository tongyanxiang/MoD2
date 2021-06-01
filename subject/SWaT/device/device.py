# The sensors would return values not in physical unit.

def usl_w(level): #ultra sonic level sensor wireless (1225->0, 0.0->31208)
	return (level - 0.0) * float(0.0-31208)/float(1225-0.0) + 31208

def usl(level): #ultra sonic level sensor (1225->3277, 0.0->16383)
	return (level - 0.0) * float(3277-16383)/float(1225-0.0) + 16383

def fi_w(flow): #flow indicator wireless (10->-15, 0.0->31208)
	return (flow - 0.0) * float(-15-31208)/float(10-0.0) + 31208

def fi(flow): #flow indicator (10->3277, 0.0->16383)
	return (flow - 0.0) * float(3277-16383)/float(10-0.0) + 16383