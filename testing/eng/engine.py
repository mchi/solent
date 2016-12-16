#
# engine (testing)
#
# // license
# Copyright 2016, Free Software Foundation.
#
# This file is part of Solent.
#
# Solent is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Solent is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Solent. If not, see <http://www.gnu.org/licenses/>.

from solent.eng import cs
from solent.eng import orb_new
from solent.util import uniq

from testing.util import clock_fake

class FakeSocket:
    def __init__(self, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.cb_tcp_connect = cb_tcp_connect
        self.cb_tcp_condrop = cb_tcp_condrop
        self.cb_tcp_recv = cb_tcp_recv

def create_fake_sid():
    return 'fake_sid_%s'%uniq()

class Engine:
    def __init__(self):
        #
        self.clock = clock_fake()
        self.events = []
        self.sent_data = []
        self.sids = {}
        #
        self.mtu = 500
    def get_clock(self):
        return self.clock
    def init_orb(self, orb_h, nearcast_schema):
        return orb_new(
            orb_h=orb_h,
            engine=self,
            nearcast_schema=nearcast_schema)
    def send(self, sid, payload):
        self.sent_data.append(payload[:])
    def open_tcp_client(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_client', addr, port) )
        #
        sid = create_fake_sid()
        self.sids[sid] = FakeSocket(
            cb_tcp_connect=cb_tcp_connect,
            cb_tcp_condrop=cb_tcp_condrop,
            cb_tcp_recv=cb_tcp_recv)
        return sid
    def open_tcp_server(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_server', addr, port) )
        #
        sid = create_fake_sid()
        self.sids[sid] = FakeSocket(
            cb_tcp_connect=cb_tcp_connect,
            cb_tcp_condrop=cb_tcp_condrop,
            cb_tcp_recv=cb_tcp_recv)
        return sid
    def close_tcp_server(self, sid):
        self.events.append( ('close_tcp_server',) )
        del self.sids[sid]
    def close_tcp_client(self, sid):
        self.events.append( ('close_tcp_client',) )
        #
        cs_tcp_condrop = cs.CsTcpCondrop()
        cs_tcp_condrop.engine = self
        cs_tcp_condrop.client_sid = sid
        cs_tcp_condrop.message = 'from fake engine, close_tcp_client'
        self.sids[sid].cb_tcp_condrop(
            cs_tcp_condrop=cs_tcp_condrop)
    def simulate_tcp_client_connect(self, server_sid, client_ip, client_port):
        s = self.sids[server_sid]
        client_sid = create_fake_sid()
        self.sids[client_sid] = FakeSocket(
            cb_tcp_connect=s.cb_tcp_connect,
            cb_tcp_condrop=s.cb_tcp_condrop,
            cb_tcp_recv=s.cb_tcp_recv)
        cs_tcp_connect = cs.CsTcpConnect()
        cs_tcp_connect.engine = self
        cs_tcp_connect.client_sid = client_sid
        cs_tcp_connect.addr = client_ip
        cs_tcp_connect.port = client_port
        s.cb_tcp_connect(
            cs_tcp_connect=cs_tcp_connect)

def engine_fake():
    ob = Engine()
    return ob

