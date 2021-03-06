#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Fugitive : Network evasion tester
# Copyright (C) 2017 Jérémy BEAUME (jeremy [dot] beaume (a) protonmail [dot] com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import scapy.all as scapy
import Queue
import threading
import sockutils

from ...utils import *


def wait_for_packet(iface, condition=None, timeout=None):
    """ Simply wait for a packet, matching condition lambda, untile timeout (return None)
    Create a temporary receiver, wait for a packet, close the receiver """
    if condition == None:
        condition = lambda x: True

    receiver = _LambdaPacketReceiver(iface=iface, condition=condition)
    pkt = receiver.recv_packet(timeout=timeout)
    receiver.close()
    return pkt


class PacketReceiver:
    """
    *Receiver of packets*

    method packet_for_me must be implemented

    Dont forget to close when done with it.
    """

    def __init__(self, iface):
        self._sniffer = _get_listener(iface)
        self._pkt_queue = Queue.Queue()
        self._sniffer.add_receiver(self)

    def recv_packet(self, timeout=None):
        """ receive a packet during the timeout
        raise IOError if timeout """
        try:
            return self._pkt_queue.get(block=True, timeout=timeout)
        except Queue.Empty:
            raise IOError("Packet receive timeout")

    def packet_for_me(self, pkt):
        """
        To be implemented is inherited classes
        return true is this packet is to be received
        """
        raise NotImplementedError

    def _give_packet(self, pkt):
        """ Adds a packet for this receiver """
        if self.packet_for_me(pkt):
            try:
                self._pkt_queue.put(pkt, block=False)
            except Queue.Full:
                # Drop packet
                print_warning("Packet dropped : queue is full")

    def close(self):
        """ Closes this receiver ( will not receive packet anymore) """
        self._sniffer.remove_receiver(self)


class _LambdaPacketReceiver(PacketReceiver):
    """ Simple PacketReceiver implementation : just a lambda for packet_for_me """

    def __init__(self, iface, condition):
        PacketReceiver.__init__(self, iface)
        self._condition = condition

    def packet_for_me(self, pkt):
        return self._condition(pkt)

#### Sniffers ####

_iface_sniffers = {}


def _get_listener(iface):
    """ Get the singleton listener for an interface
    If none exists : create one, and start listening """
    if iface in _iface_sniffers:
        return _iface_sniffers[iface]
    else:
        l = _IfaceSniffer(iface)
        _iface_sniffers[iface] = l
        l.start()  # always sniff the interfaces
        return l


class _IfaceSniffer:
    """
    Private class, listening to an interface
    Should not ne intanciate as is : use _get_listener if needed (Singleton)

    When receiving a packet, circle through receivers, and calls
    _give_packet on them.

    Filter inbound packet based on interface MAC address
    """

    def __init__(self, iface):
        self._iface = iface
        self._mac = sockutils.get_iface_mac(self._iface)
        self._started = False

    def start(self):
        """ Start a new thread to sniff the interface """
        if not self._started:
            self._started = True
            self._receivers = []
            t = threading.Thread(target=_IfaceSniffer_thread, args=(self,))
            t.setDaemon(True)
            t.start()

    def add_receiver(self, receiver):
        self._receivers.append(receiver)

    def remove_receiver(self, receiver):
        self._receivers.remove(receiver)

    def handle_packet(self, pkt):
        """ Receive a sniffed packet """
        # check that itś an inbound packet
        if pkt[scapy.Ether].dst == self._mac:
            for receiver in self._receivers:  # if itś a response for the receiver
                receiver._give_packet(pkt)  # store it in its queue


def _IfaceSniffer_thread(sniffer):
    """ Thread de sniff scapy """
    #print_notice("Start sniffing on "+ sniffer._iface)
    scapy.sniff(iface=sniffer._iface,
                prn=lambda pkt: sniffer.handle_packet(pkt))
