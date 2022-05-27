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
                # We iterate over all participants, and send shares. When the id is ourselves, we store the share.
                if self.protocol_spec.participant_ids[i] == self.client_id:
                    self.myShares[secret.id] = shares[i]
                else:    
                    self.comm.send_private_message(self.protocol_spec.participant_ids[i], secret.id, json.dumps(shares[i]))
        
        # Then, we compute the protocol expression for the first round
        myShare = self.process_expression(self.protocol_spec.expr) 

        # Final round, we publish the obtained value and compute the result with the other published values
        self.comm.publish_message("final", json.dumps(myShare))
        share_list = list()
        for participant_id in self.protocol_spec.participant_ids:
            if participant_id  == self.client_id:
                share_list.append(myShare)
            else:    
                share_list.append(json.loads(self.comm.retrieve_public_message(participant_id, "final")))
        return reconstruct_secret(share_list)        


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ) -> Share:
        if isinstance(expr, Addition):
            left = self.process_expression(expr.expr1)
            right = self.process_expression(expr.expr2)

            # If client is client 0
            if self.client_id == self.protocol_spec.participant_ids[0]:
                return left + right
            # Otherwise    
            else:
                if (isinstance(left, Scalar) and isinstance(right, Secret)):
                    return right
                if isinstance(left, Secret) and isinstance(right, Scalar):
                    return left  
                if isinstance(left, Secret) and isinstance(right, Secret):
                    return left + right
                else:
                    return Share(0)             

        if isinstance(expr, Secret):
            if expr in (list(self.value_dict.keys())):
                return self.myShares[expr.id]
            else:
                return json.loads(self.comm.retrieve_private_message(expr.id))    

        if isinstance(expr, Scalar):
            return Share(expr.value)

        if isinstance(expr, Substraction):
            left = self.process_expression(expr.expr1)
            right = self.process_expression(expr.expr2)

            if self.client_id == self.protocol_spec.participant_ids[0]:
                return left - right  
            else:
                if (isinstance(left, Scalar) and isinstance(right, Secret)):
                    return Share(0) - right
                if isinstance(left, Secret) and isinstance(right, Scalar):
                    return left  
                if isinstance(left, Secret) and isinstance(right, Secret):
                    return left - right
                else:
                    return Share(0)     

        if isinstance(expr, Multiplication):
            left = self.process_expression(expr.expr1)
            right = self.process_expression(expr.expr2)

            if isinstance(left, Secret) and isinstance(right, Secret):
                a, b, c = self.comm.retrieve_beaver_triplet_shares(self.protocol_spec.expr.id)
                share_x = left - Share(a)
                share_y = right - Share(b)
                self.comm.publish_message("share_x", json.dumps(share_x))
                self.comm.publish_message("share_y", json.dumps(share_y))

                share_x_list = list()
                share_y_list = list()
                for participant_id in self.protocol_spec.participant_ids:
                    if participant_id  == self.client_id:
                        share_x_list.append(share_x)
                        share_y_list.append(share_y)
                    else:    
                        share_x_list.append(json.loads(self.comm.retrieve_public_message(participant_id, "share_x")))
                        share_y_list.append(json.loads(self.comm.retrieve_public_message(participant_id, "share_y")))
                share_x_val = reconstruct_secret(share_x_list)
                share_y_val = reconstruct_secret(share_y_list)
                share_z = c + left * share_y_val + right * share_x_val
                if self.client_id == self.protocol_spec.participant_ids[0]:
                    return share_z - share_x_val * share_y_val
                return share_z    

            else:
                return left * right    
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.
        pass

    # Feel free to add as many methods as you want.