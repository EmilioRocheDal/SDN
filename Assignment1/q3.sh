#!/bin/bash

#H2 to H6 and back direction
ovs-ofctl add-flow s2 in_port=1,actions=output:3
ovs-ofctl add-flow s2 in_port=3,actions=output:1
ovs-ofctl add-flow s3 in_port=3,actions=output:4
ovs-ofctl add-flow s3 in_port=4,actions=output:3
ovs-ofctl add-flow s4 in_port=2,actions=output:4
ovs-ofctl add-flow s4 in_port=4,actions=output:2
ovs-ofctl add-flow s6 in_port=2,actions=output:1
ovs-ofctl add-flow s6 in_port=1,actions=output:2




