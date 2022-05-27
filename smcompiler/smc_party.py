"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import json
from typing import Dict

from sympy import Mul

from communication import Communication
from expression import (
    Addition,
    Expression,
    Multiplication,
    Secret,
    Scalar,
    Substraction
)
from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
)
from Crypto.Util import number

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict

        # This dict contains the corresponding part of the client for each secret when sharing it
        self.myShares = {}

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """

        # Firstly, the client shares all his secrets with the other parties, using their id as the channel
        for secret, value in self.value_dict.items():
            shares = share_secret(value, len(self.protocol_spec.participant_ids))
            for i in range(len(self.protocol_spec.participant_ids)):
                if self.protocol_spec.participant_ids[i] == self.client_id:
                    self.myShares[secret.id] = shares[i]
                else:    
                    self.comm.send_private_message(self.protocol_spec.participant_ids[i], secret.id, json.dumps(shares[i]))
        
        # Then, we compute the protocol expression for the first round
        myShare = self.process_expression(self.protocol_spec.expr) 

        # Final round, we publish the obtained value and compute the result with the other published values
        self.comm.publish_message("final", json.dumps(myShare))
        shareList = list()
        for participant_id in self.protocol_spec.participant_ids:
            if participant_id  == self.client_id:
                shareList.append(myShare)
            else:    
                shareList.append(json.loads(self.comm.retrieve_public_message(participant_id, "final")))
        return reconstruct_secret(shareList)        


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ) -> Share:
        
        if isinstance(expr, Addition):
            share = self.process_expression(expr.expr1)
            return share + self.process_expression(expr.expr2)

        if isinstance(expr, Secret):
            if (list(self.value_dict.items())[0][0]).id == expr.id:
                return self.myShares[expr.id]
            else:
                return json.loads(self.comm.retrieve_private_message(expr.id))    

        if isinstance(expr, Scalar):
            return Share(expr.value)

        if isinstance(expr, Substraction):
            share = self.process_expression(expr.expr1)
            return share - self.process_expression(expr.expr2)

        if isinstance(expr, Multiplication):
            share_x = self.process_expression(expr.expr1)
            share_y = self.process_expression(expr.expr2)
            a, b, c = self.comm.retrieve_beaver_triplet_shares(self.protocol_spec.expr.id)
            self.comm.publish_message("final", json.dumps(share_x - a))
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.
        pass

    # Feel free to add as many methods as you want.