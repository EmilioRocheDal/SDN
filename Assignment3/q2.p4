/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

/* ---------------------------------------
    STEP 1: TODO - Define your own header
   --------------------------------------- */

// ++++++++++++++++++++++++++++
// |          32 bits         |
// ++++++++++++++++++++++++++++
header stats_t {
    bit<48>	  timeStamp;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    udp_t		 udp;
    stats_t time;

/* -------------------------------------------------------------
    STEP 2: TODO - Add your header to the packet header vector
   ------------------------------------------------------------- */
	stats_t		 switchStats;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
	//Writing the packet parser (Q1 step 1 - start, parse_ethernet, parse_ipv4, parse_udp)
	state start {
		transition parse_ethernet;
	}

	state parse_ethernet {
		packet.extract(hdr.ethernet);
		transition parse_ipv4;
	}	

	state parse_ipv4 {
		packet.extract(hdr.ipv4);
		transition parse_udp;
	}

    	state parse_udp {
		packet.extract(hdr.udp);
		transition accept;
	}

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
  //register creation
  register<bit<48>>(16384) last_seen;

    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(egressSpec_t port, bit<48> newDstMac) {
		standard_metadata.egress_spec = port;
		//here it is set
		hdr.ethernet.dstAddr = newDstMac;
    }
    table ipv4_lpm {
		key = {
			hdr.ipv4.dstAddr : exact;
		}

		actions = {
			drop;
			ipv4_forward;
		}

		size = 10;
    }

    apply {

      hdr.time.setValid();
      if (hdr.ipv4.isValid()) {
          ipv4_lpm.apply();

      }
      bit<48> prev_time;
      last_seen.read(prev_time, hdr.ipv4.dstAddr);
      hdr.time.timeStamp = standard_metadata.ingress_global_timestamp - prev_time;
      last_seen.write(hdr.ipv4.dstAddr, standard_metadata.ingress_global_timestamp);
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {	
    		//Write packet deparser (Q1 step 4)
		packet.emit(hdr.ethernet);
		packet.emit(hdr.ipv4);
		packet.emit(hdr.udp);
		packet.emit(hdr.time);

    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
