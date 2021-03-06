#!/usr/bin/python

from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls

#--------------------------------------
# STEP 2c: add dead dispatcher
#-------------------------------------
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, DEAD_DISPATCHER

from ryu.controller import ofp_event

from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

#--------------------------------------
# STEP 1: import hub library
#--------------------------------------
from ryu.lib import hub

import networkx as nx

class Controller1(app_manager.RyuApp):

	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	def __init__(self, *args, **kwargs):
		super(Controller1, self).__init__(*args, **kwargs)
		self.topology_api_app = self
		self.net = nx.DiGraph()

		#--------------------------------------
		# STEP 2a: store switch datapaths
		#--------------------------------------
		self.datapaths = {}

		#--------------------------------------
		# STEP 3: start monitor thread
		#--------------------------------------
		self.monitor_thread = hub.spawn(self._monitor)


	#--------------------------------------
	# STEP 2b: store switch datapaths
	#--------------------------------------
	@set_ev_cls(ofp_event.EventOFPStateChange,
				[MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		if ev.state == MAIN_DISPATCHER:
			if datapath.id not in self.datapaths:
				self.logger.debug('register datapath: %016x', datapath.id)
				self.datapaths[datapath.id] = datapath
		elif ev.state == DEAD_DISPATCHER:
			if datapath.id in self.datapaths:
				self.logger.debug('unregister datapath: %016x', datapath.id)
				del self.datapaths[datapath.id]

		
	@set_ev_cls(event.EventSwitchEnter)
	def get_topology_data(self, ev):
		switch_list = get_switch(self.topology_api_app, None)
		switches = [switch.dp.id for switch in switch_list]
		self.net.add_nodes_from(switches)

		link_list = get_link(self.topology_api_app, None)

		for link in link_list:
			self.net.add_edge(link.src.dpid, link.dst.dpid, port=link.src.port_no)
			self.net.add_edge(link.dst.dpid, link.src.dpid, port=link.dst.port_no)


	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		#Process switch connection 
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto	
		parser = datapath.ofproto_parser

		#Add default rule
		match = parser.OFPMatch()	
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
						  ofproto.OFPCML_NO_BUFFER)]
			
		self.add_flow(datapath, 0, match, actions)


	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto

		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocol(ethernet.ethernet)

		dpid = datapath.id
		src = eth.src
		dst = eth.dst

		#Add end hosts to discovered topo
		if src not in self.net:
			self.net.add_node(src)
			self.net.add_edge(dpid,src,port=msg.match['in_port'])
			self.net.add_edge(src,dpid)
		
		elif src in self.net and dst in self.net:

			#Add forwarding rule
			parser = datapath.ofproto_parser
			
			path = nx.shortest_path(self.net,src,dst)

			match = parser.OFPMatch(eth_dst=dst, eth_src=src)	
			for id in range(1, len(path)-1):
				current = path[id]
				next = path[path.index(current)+1]
				datapath = self.datapaths[current]
			#gets output port for the next hop
				out_port = self.net[current][next]['port']
				actions = [parser.OFPActionOutput(out_port)]
			#add flow rules for all switches by iterating
				self.add_flow(datapath, 1, match, actions)

			#Forward original packet
			parser = datapath.ofproto_parser

			out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.match['in_port'], actions=actions)
			datapath.send_msg(out)


	def add_flow(self, datapath, priority, match, actions):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		#Construct flow_mod message and send it
		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
						     actions)]

		mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
					match=match, instructions=inst)

		datapath.send_msg(mod)


	#--------------------------------------
	# STEP 4: define monitoring function
	#--------------------------------------
	def _monitor(self):
		while True:
			for dp in self.datapaths.values():
				if(dp.id == 5):
					self._request_stats(dp)
			hub.sleep(5)


	#--------------------------------------
	# STEP 5: send stats request
	#--------------------------------------
	def _request_stats(self, datapath):
		self.logger.debug('send stats request: %016x', datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		req = parser.OFPPortStatsRequest(datapath)
		datapath.send_msg(req)


	#--------------------------------------
	# STEP 6: process stats reply
	#--------------------------------------
	@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
	def _flow_stats_reply_handler(self, ev):

		print('--------------------------'
			  '--------------------------'
			  '---------')
		print('\t\t >>>>> PORT STATS - S%d <<<<<' %ev.msg.datapath.id)
		print('--------------------------'
			  '--------------------------'
			  '---------')


		self.logger.info('port. no          '
						'rx_packets')
		self.logger.info('--------------'
						'     --------')

		body = ev.msg.body

		for stat in body:
			self.logger.info('%14d %10d',stat.port_no, stat.rx_packets)
		
		print('\n')







