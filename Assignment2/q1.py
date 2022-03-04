#!/usr/bin/python

from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller import ofp_event

from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

import networkx as nx

class Controller1(app_manager.RyuApp):

	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	def __init__(self, *args, **kwargs):
		super(Controller1, self).__init__(*args, **kwargs)
		self.topology_api_app = self
		self.net = nx.DiGraph()
		self.switches = {}

	#get topology information for my network
	@set_ev_cls(event.EventSwitchEnter)
	def get_topology_data(self, ev):
		switch_list = get_switch(self.topology_api_app, None)
		switches = [switch.dp.id for switch in switch_list]
		self.net.add_nodes_from(switches)

		link_list = get_link(self.topology_api_app, None)

		for link in link_list:
			self.net.add_edge(link.src.dpid, link.dst.dpid, port=link.src.port_no)
			self.net.add_edge(link.dst.dpid, link.src.dpid, port=link.dst.port_no)

	#any features the switch has and any behavior
	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		#Process switch connection 
		datapath = ev.msg.datapath
		self.switches[datapath.id] = datapath
		ofproto = datapath.ofproto	
		parser = datapath.ofproto_parser

		#Add default rule - submit packet to controller when doesn't know what to do with it
		#wildcard match
		match = parser.OFPMatch()
		#OFPP_CONTROLLER sends it to controller	
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
						  				  ofproto.OFPCML_NO_BUFFER)]
			
		self.add_flow(datapath, 0, match, actions)


	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocol(ethernet.ethernet)

		dpid = datapath.id
		src = eth.src
		dst = eth.dst

		if src not in self.net:
			self.net.add_node(src)
			self.net.add_edge(dpid,src,port=ofproto.OFPXMT_OFB_IN_PHY_PORT)
			self.net.add_edge(src,dpid)

		#goes in if dst is in,
		if dst in self.net:
			#-----------------------------------------------------------
			# STEP 1: TODO - compute shortest path between src and dst (reference: https://sdn-lab.com/2014/12/25/shortest-path-forwarding-with-openflow-on-ryu/ )
			#-----------------------------------------------------------
			#gets the shortest path using the network x method (https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
			path = nx.shortest_path(self.net,src,dst)
			#print(path) #prints out path
			#------------------------------------------------------------------------
			# STEP 2: TODO - install a routing rule for every switch in the path
			#------------------------------------------------------------------------
			#match based of ethernet src and ethernet dst
			originalDatapath = msg.datapath
			match = parser.OFPMatch(eth_dst=dst, eth_src=src)
			for id in range(1, len(path)-1):
				current = path[id]
				next = path[path.index(current)+1]
				datapath = self.switches[current]
			#gets output port for the next hop
				out_port = self.net[current][next]['port']
				actions = [parser.OFPActionOutput(out_port)]
			#add flow rules for all switches by iterating
				self.add_flow(datapath, 1, match, actions)
				#print("added base rule for ", id)
			#------------------------------------------------------------------------
			# STEP 3: TODO - install a firewall rule in the ingress switch (i.e., 
			#                first switch in the path), if needed
			#------------------------------------------------------------------------
			srcHost = path[1]
			dstHost = path[-2]

			parser = originalDatapath.ofproto_parser
			out = parser.OFPPacketOut(datapath=originalDatapath, buffer_id=msg.buffer_id, in_port=msg.match['in_port'], actions=actions)
			if self.isEven(srcHost):
				if not self.isEven(dstHost):
					actions = []
					self.add_flow(originalDatapath, 2, match, actions)
				else:
					originalDatapath.send_msg(out)
			#if src is odd
			else:
				if self.isEven(dstHost):
					actions = []
					self.add_flow(originalDatapath, 2, match, actions)
				else:
					originalDatapath.send_msg(out)
			
			
				
	def isEven(self, nodeId):
		if nodeId % 2 == 0:
			return True
		else:
			return False

	def add_flow(self, datapath, priority, match, actions):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		#Construct flow_mod message and send it
		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
						     actions)]

		mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
					match=match, instructions=inst)

		datapath.send_msg(mod)











